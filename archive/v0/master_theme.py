import pandas as pd
import json
import os
from datetime import datetime
import openai
from openai import OpenAI
import streamlit as st
from llama_index.core import VectorStoreIndex, Document
from llama_index.core.vector_stores import SimpleVectorStore
from llama_index.core.storage.storage_context import StorageContext
from llama_index.embeddings.openai import OpenAIEmbedding
from pymongo import MongoClient
import numpy as np
from numpy.linalg import norm
import PyPDF2
from io import BytesIO
import base64
import modules.main as main
from modules.models import LLMModelInterface

UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)

MONGO_URI = os.getenv('MONGO_URI')
MONGO_URI = "mongodb+srv://akhilvaidya22:qN2dxc1cpwD64TeI@digital-nova.cbbsn.mongodb.net/?retryWrites=true&w=majority&appName=digital-nova"

database_name = 'digital_nova'
client = MongoClient(MONGO_URI)
db = client[database_name]
themes_collection = db['themes']
corpus_collection = db['corpus']
user = db['users']


# Function to fetch data from Perplexity API
def fetch_perplexity_data(api_key, topic):
    headers = {
        "accept": "application/json",
        "content-type": "application/json",
        "authorization": f"Bearer {api_key}"
    }
    messages = [
        {
            "role": "system",
            "content": (
                "You are a expert providing official information about the given topic. Provide only verified information with atleast 3 working reference links for citations."
            ),
        },
        {
            "role": "user",
            "content": topic
        },
    ]
    
    try:
        client = OpenAI(api_key=api_key, base_url="https://api.perplexity.ai")
        response = client.chat.completions.create(
            model="llama-3.1-sonar-small-128k-online",
            messages=messages,
        )
        content = response.choices[0].message.content
        return content
    except Exception as e:
        st.error(f"Failed to fetch data from Perplexity API: {e}")
        return ""

def structure_data(api_key, generated_text, columns, model):
    prompt = f"You are an AI that structures data into JSON format (list of python dictionaries) for converting unstructured text data into tables. Ensure that you have atlest as many rows in the output as much mentioned in the input text. Return the data in such a way that it is a list of dictionaried that can be converted to a pandas dataframe directly. You are given a large amount of data that can be structured into a table with many rows. Structure the following data into a list of JSON format with columns: {columns}. Data: {generated_text}. Ensure that you only output the data in JSON format without any other text at all, not even backtics `` and the word JSON. Do not include any other information in the output. Start your output string with an opening square brace [ and end with a closing square brace ] as it's last characcter of the srting (strictly follow this rule). Ensure that the list of JSON/python dictionaries can be directly parsed to a dataframe without any additional text."
    interface = LLMModelInterface()
    if model == "Gemini":
        structured_data = interface.call_gemini(prompt, api_key)
        if structured_data[0] != '[':
            structured_data = '[' + structured_data + ']'
        try:
            json_op = json.loads(structured_data)
            return json_op
        except Exception as e:
            st.error(f"Failed to structure data using Gemini: {e}")
            print(e)
            return []
    
    messages = [
        {
            "role": "system",
            "content": "You are an AI that structures data into JSON format for converting unstructured text data into tables. Ensure that you have atlest as many rows in the output as much mentioned in the input text. Return the data in such a way that it is a list of dictionaried that can be converted to a pandas dataframe directly."
        },  
        {
            "role": "user",
            "content": prompt
        },
    ]
    
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.1,
        )
        json_content = response.choices[0].message.content
        return json.loads(json_content)
    except Exception as e:
        st.error(f"Failed to structure data using GPT-4o Mini: {e}")
        return []


def create_embeddings(text, openai_api_key):
    client = OpenAI(api_key=openai_api_key)
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

def generate_theme_title(api_key, text):
    prompt = f"Provide a 2-3 word title that captures the main theme of the following text: {text} Return only the 2 3 word string and nothing else. Do not include any other information in the output."
    messages = [
        {
            "role": "system",
            "content": "You are an AI that generates concise titles for text content."
        },
        {
            "role": "user",
            "content": prompt
        },
    ]
    
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.1,
        )
        theme_title = response.choices[0].message.content.strip()
        return theme_title
    except Exception as e:
        st.error(f"Failed to generate theme title using GPT-4o Mini: {e}")
        return "Unnamed Theme"

# Function to store vectors in MongoDB Atlas
def store_vectors_mongodb(df, mongodb_uri, openai_api_key, theme_title):
    try:
        # Connect to MongoDB Atlas
        client = MongoClient(mongodb_uri)
        db = client['digital_nova']
        collection = db['cell_vectors']
        
        # Create indices for vector search
        collection.create_index([("vector", "2dsphere")])
        
        # Process each cell in the dataframe
        vectors_data = []
        for index, row in df.iterrows():
            for column in df.columns:
                cell_text = str(row[column])
                vector = create_embeddings(cell_text, openai_api_key)
                
                vector_doc = {
                    'theme_title': theme_title,
                    'row_id': index,
                    'column_name': column,
                    'text': cell_text,
                    'vector': vector,
                    'timestamp': datetime.now()
                }
                vectors_data.append(vector_doc)
        
        # Batch insert all vectors
        if vectors_data:
            collection.insert_many(vectors_data)
            return len(vectors_data)
        
        return 0
    
    except Exception as e:
        raise Exception(f"Failed to store vectors in MongoDB: {e}")
    # finally:
    #     client.close()

def cosine_similarity(v1, v2):
    """Calculate cosine similarity between two vectors"""
    dot_product = np.dot(v1, v2)
    norm_product = norm(v1) * norm(v2)
    return dot_product / norm_product if norm_product != 0 else 0

def search_vectors(query_text, k, mongodb_uri, openai_api_key):
    """
    Search for k most similar vectors in the MongoDB store
    """
    try:
        # Create embedding for the query
        query_vector = create_embeddings(query_text, openai_api_key)
        # Connect to MongoDB
        client = MongoClient(mongodb_uri)
        db = client['digital_nova']
        collection = db['cell_vectors']
        
        # Get all documents (we'll optimize this later if needed)
        all_docs = list(collection.find({}))
        
        # Calculate similarities
        similarities = []
        for doc in all_docs:
            similarity = cosine_similarity(query_vector, doc['vector'])
            similarities.append({
                'similarity': similarity,
                'text': doc['text'],
                'column_name': doc['column_name'],
                'row_id': doc['row_id']
            })
        
        # Sort by similarity and get top k
        similarities.sort(key=lambda x: x['similarity'], reverse=True)
        return similarities[:k]
    
    except Exception as e:
        raise Exception(f"Failed to search vectors: {e}")
    # finally:
    #     client.close()

def process_pdf_and_create_vectors(file_path, file_name, openai_api_key, chunk_size=50):
    """
    Process a PDF file and create vectors for chunks of text
    """
    vectors_data = []
    try:
        # Open and read PDF
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            full_text = ""
            
            # Extract text from each page
            for page in pdf_reader.pages:
                full_text += page.extract_text() + " "
            
            # Split text into chunks
            words = full_text.split()
            chunks = []
            current_chunk = []
            
            for word in words:
                current_chunk.append(word)
                if len(current_chunk) >= chunk_size:
                    chunks.append(' '.join(current_chunk))
                    current_chunk = []
            
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            
            # Create vectors for each chunk
            for i, chunk in enumerate(chunks):
                # print("calling openai")
                vector = create_embeddings(chunk, openai_api_key)
                vector_doc = {
                    'file_name': file_name,
                    'chunk_index': i,
                    'text': chunk,
                    'vector': vector,
                    'timestamp': datetime.now()
                }
                vectors_data.append(vector_doc)
                
        return vectors_data
    except Exception as e:
        raise Exception(f"Error processing PDF {file_name}: {e}")
    
def structure_document_content(api_key, document_text, columns):
    """
    Structure a single document's content into the specified columns using OpenAI API
    """
    # columns = str(columns)
    prompt = f"""Structure the following document content into a single row with these columns: {columns}
    The if there is a column called goals or keywords, then goals colums should contain the main theme goals that can be identified, keywords should list out atleast 8 keywords per goal.
    
    Document content: {document_text}
    Ensure that your response is extremely detailed and covers every single important point from the document. If it has names or dates or project names mentioned, ensure that they are included in the response.
    Return only a list of flat JSON objects with the specified columns as keys and appropriate content as values. The values should either be strings or numbers, no nested objects or lists at all. Note that this JSON will be passed on to pandas to convert to a dataframe, so create the dataframe accordingly. DO NOT USE THE WORD JSON IN RESPONSE OR EVEN BACKTICS ```. Start and end your response with curley beackets. 
    Ensure the response can be directly parsed as JSON without any additional text."""
    
    messages = [
        {
            "role": "system",
            "content": "You are an AI that structures document content into specific columns for data analysis. You MUST respond in a JSON format only, and the JSON should be directly convertible to a pandas DataFrame."
        },
        {
            "role": "user",
            "content": prompt
        }
    ]
    
    try:
        client = OpenAI(api_key=api_key)
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=messages,
            temperature=0.1
        )
        return json.loads(response.choices[0].message.content)
    except Exception as e:
        st.error(f"Failed to structure document content: {e}")
        return None
    
def csv_analytics(api_key, user_prompt, column_names, selected_column, dataframe):
    """
    Analyze a selected column in a dataframe using an LLM and generate new columns based on the analysis.

    Parameters:
    - api_key (str): OpenAI API key.
    - user_prompt (str): The user's prompt or specific analytical requirements.
    - column_names (str): Comma-separated string of new column names to be generated.
    - selected_column (str): The name of the column in the dataframe to analyze.
    - dataframe (pd.DataFrame): The pandas DataFrame containing the data.

    Returns:
    - pd.DataFrame: A new DataFrame with the generated columns appended.
    """

    # Prepare the list of new columns
    new_columns = [col.strip() for col in column_names.split(",")]

    # Initialize a list to store the results
    results = []

    # Iterate over each row in the selected column
    for index, row in dataframe.iterrows():
        text_to_analyze = str(row[selected_column])

        # Construct the prompt using the provided template
        # Input Parameters
        user_prompt_input = user_prompt
        research_paper_text = text_to_analyze
        paper_section = selected_column
        required_output_columns = new_columns

        # Assemble the detailed prompt
        prompt = f"""
Perform a detailed, systematic analysis of the following section of a research paper, extracting key insights based on the user's requirements.

User Prompt: {user_prompt_input}
Research Paper Text: {research_paper_text}
Paper Section: {paper_section}
Required Output Columns: {required_output_columns}

You are to analyze the 'Research Paper Text' based on the 'User Prompt' and extract the insights specified in 'Required Output Columns'.

Detailed Instructions:
1. **Contextual Analysis**
   - Carefully read and comprehend the provided research paper text.
   - Identify the core context, research objectives, and key arguments.
   - Align analysis with the specified paper section.

2. **Insight Extraction Methodology**
   - For each required output column:
     a. Conduct a deep, nuanced analysis of the text.
     b. Extract precise, evidence-based insights.
     c. Ensure insights are directly derived from the source text.
     d. Maintain academic rigor and objectivity.

3. **JSON Response Requirements**
   - Generate a structured JSON response.
   - Include ALL specified columns, using the exact names provided in 'Required Output Columns'.
   - Ensure that you are using the exact names that are mentioned in the user's input key list.
   - The values of the keys should be plain text strings only (no nested objects or lists).
   - Note that this JSON will later be used to populate a table having the user mentioned column names, so please use the same key/column names only.
   - **DO NOT INCLUDE THE WORD JSON IN THE OUTPUT STRING, DO NOT INCLUDE BACKTICKS (```) IN THE OUTPUT, AND DO NOT INCLUDE ANY OTHER TEXT, OTHER THAN THE ACTUAL JSON RESPONSE. START THE RESPONSE STRING WITH AN OPEN CURLY BRACE {{ AND END WITH A CLOSING CURLY BRACE }}.**
   - Populate each column with:
     * Concise, informative text.
     * Direct insights from the research paper.
     * Clear, academic language.
     * Minimal interpretation beyond the text's explicit content.
     * Only use pure normal strings as the JSON values, no objects or lists.

4. **Quality Assurance Checks**
   - Verify that insights are:
     * Directly supported by the text.
     * Relevant to the specified section.
     * Aligned with the user's analytical requirements.
     * Free from external assumptions or unsupported claims.
"""
        try:
            messages = [
                {
                    "role": "system",
                    "content": "You are an AI that is an expert on research papers for data analysis. You MUST respond in a JSON format only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
            # Call the OpenAI API
            client = OpenAI(api_key=api_key)
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.1
            )

            # Extract the assistant's reply
            reply = response.choices[0].message.content.strip()

            # Parse the JSON response
            data = json.loads(reply)

            # Ensure all required columns are present
            missing_columns = [col for col in new_columns if col not in data]
            if missing_columns:
                # Handle missing columns
                for col in missing_columns:
                    data[col] = None

            # Add the data to the results list
            results.append(data)

        except Exception as e:
            print(f"Error processing row {index}: {e}")
            # Append None or empty dictionary to keep the index alignment
            empty_data = {col: None for col in new_columns}
            results.append(empty_data)

    # Convert results to DataFrame
    results_df = pd.DataFrame(results, columns=new_columns)

    # Reset indices to align the dataframes
    dataframe.reset_index(drop=True, inplace=True)
    results_df.reset_index(drop=True, inplace=True)

    # Concatenate the original dataframe with the new columns
    final_df = pd.concat([dataframe, results_df], axis=1)

    return final_df

def read_pdf_content(file_path):
    """
    Read and extract text content from a PDF file
    """
    try:
        with open(file_path, 'rb') as file:
            pdf_reader = PyPDF2.PdfReader(file)
            full_text = ""
            for page in pdf_reader.pages:
                full_text += page.extract_text() + " "
            return full_text.strip()
    except Exception as e:
        st.error(f"Failed to read PDF content: {e}")
        return None

def themes_main(username):
    # Initialize session state variables
    if "perplexity_text" not in st.session_state:
        st.session_state.perplexity_text = ""
    if "generated_text" not in st.session_state:
        st.session_state.generated_text = ""
    if "show_buttons" not in st.session_state:
        st.session_state.show_buttons = False
    if "dataframe" not in st.session_state:
        st.session_state.dataframe = None
    if "vector_store_created" not in st.session_state:
        st.session_state.vector_store_created = False
    if "theme_title" not in st.session_state:
        st.session_state.theme_title = ""
    if "current_theme" not in st.session_state:
        st.session_state.current_theme = ""
    
    tab1, tab2 = st.tabs(["Theme Generation", "Doc Theme Generation"])

    user = db['users']
    current_user = user.find_one({'username': username})
    if current_user:
        api_keys = current_user.get('api_keys', {})
        openai_key = api_keys.get('openai', "")
        perplexity_key = api_keys.get('perplexity', "")
        gemini_key = api_keys.get('gemini', "")
    else:
        api_keys = {}

    with tab1:
        if perplexity_key:
            st.info("""
            **Theme Generation Guidelines**

            When generating a theme, please include the following elements in your prompt:

            - **Theme**: The main subject or overarching idea.
            - **Subthemes**: Related topics that fall under the main theme.
            - **Description**: Brief explanations for each subtheme.
            - **Keywords**: Important terms associated with each subtheme.
            - **Examples**: Illustrations or scenarios for clarity.
            """)
            theme_name = st.text_input("Enter a theme name:")
            st.session_state.current_theme = theme_name
            topic = st.text_input("Enter a topic:")
            
            if st.button("Generate"):
                if topic:

                    st.session_state.generated_text = fetch_perplexity_data(perplexity_key, topic)
                    if st.session_state.generated_text:
                        st.markdown(st.session_state.generated_text)
                        st.session_state.show_buttons = True

                        # Store query and response in MongoDB
                        chat_logs_collection = db['chat_logs']
                        chat_log_doc = {
                            'username': username,
                            'theme': st.session_state.current_theme,
                            'query': topic,
                            'response': st.session_state.generated_text,
                            'timestamp': datetime.now()
                        }
                        chat_logs_collection.insert_one(chat_log_doc)
                else:
                    st.warning("Please enter a topic to generate text.")

            # Show Keep/Discard buttons only after generation
            if st.session_state.show_buttons:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Keep"):
                        st.session_state.perplexity_text = st.session_state.generated_text
                        st.session_state.generated_text = ""  # Clear generated text
                        st.session_state.show_buttons = False  # Hide buttons
                        st.success("Text kept successfully!")
                        st.rerun()
                with col2:
                    if st.button("Discard"):
                        st.session_state.generated_text = ""  # Clear generated text
                        st.session_state.show_buttons = False  # Hide buttons
                        st.warning("Text discarded. Please enter a new topic.")
                        st.rerun()

            # Show the structuring options only if there's kept text
            if st.session_state.perplexity_text:
                st.subheader("Stored Text")
                st.markdown(st.session_state.perplexity_text)
                
                # columns = st.text_input("Enter columns (comma-separated):")
                columns = "Goal, Description, Keywords, Reference links, Examples"
                st.info("Columns: Goal, Description, Keywords, Reference links, Examples")
                model = st.selectbox("Select a model for analysis", ["GPT-4o", "Gemini"])

                if st.button("Structure Data"):
                    if columns:
                        if model == "Gemini":
                            structured_data = structure_data(gemini_key, st.session_state.perplexity_text, columns, model)
                        elif model == "GPT-4o":
                            structured_data = structure_data(openai_key, st.session_state.perplexity_text, columns, model)
                        if structured_data:
                            st.session_state.dataframe = pd.DataFrame(structured_data)
                            st.dataframe(st.session_state.dataframe)
                            # theme_title = generate_theme_title(openai_key, st.session_state.perplexity_text)
                            theme_title = st.session_state.current_theme
                            st.session_state.theme_title = theme_title
                    
                        
                        theme_data = {
                            'username': username,
                            'theme_title': theme_title,
                            'structured_data': structured_data,
                            'created_at': datetime.now(),
                            'updated_at': datetime.now()
                        }
                        
                        themes_collection.insert_one(theme_data)
                        st.success(f"Structured table stored in MongoDB with theme title '{theme_title}' successfully!")
                    else:
                        st.warning("Please enter columns to structure data.")

            # Add Chat History expander
            if st.session_state.current_theme:
                with st.expander("Chat History"):
                    chat_logs_collection = db['chat_logs']
                    chat_logs = chat_logs_collection.find({
                        'username': username,
                        'theme': st.session_state.current_theme
                    }).sort('timestamp', -1)
                    for chat in chat_logs:
                        st.markdown(f"**You:** {chat['query']}")
                        st.markdown(f"**Perplexity:** {chat['response']}")

        else:
            st.warning("Please set your Perplexity API key in your profile settings.")

    # Vector Search Tab
    # with tab2:
    #     st.subheader("Corpus Upload")
    #     st.info("""
    #     **Corpus Structuring Guidelines**

    #     - **File Format**: Please upload your documents in **PDF format** for text parsing. If your documents are in Excel or other formats, kindly convert them to PDF before uploading.
    #     - **Content Quality**: Ensure that your PDFs contain selectable text for accurate text extraction.
    #     - **Naming Convention**: Use descriptive file names to help organize your corpus effectively.

    #     *Note*: Properly structured corpora improve the performance of vector searches and theme analytics.
    #     """)
        
    #     # Create uploads directory if it doesn't exist

        
    #     # Corpus name input
    #     corpus_name = st.text_input("Enter a name for your corpus:")
        
    #     # File uploader
    #     uploaded_files = st.file_uploader(
    #         "Upload PDF files", 
    #         type=["pdf"],
    #         accept_multiple_files=True
    #     )
    #     saved_files = []
    #     all_vectors = []
        
    #     if corpus_name and uploaded_files:

    #         if st.button("Save Corpus"):
    #             try:
    #                 # Save files and collect filenames
                    
    #                 for uploaded_file in uploaded_files:
    #                     # Create a filename that includes corpus name for organization
    #                     safe_corpus_name = "".join(c for c in corpus_name if c.isalnum() or c in (' ', '-', '_')).strip()
    #                     filename = f"{safe_corpus_name}_{uploaded_file.name}"
    #                     file_path = os.path.join(UPLOAD_DIR, filename)
                        
    #                     # Save file to uploads directory
    #                     with open(file_path, "wb") as f:
    #                         f.write(uploaded_file.getbuffer())
    #                     saved_files.append(filename)

    #                     # Process PDF and create vectors

    #                 # if st.button("Process PDF and Create Vectors", key=filename):
    #                 if True:
    #                     for uploaded_file in uploaded_files:

    #                         with st.spinner(f"Processing {filename}..."):
    #                             vectors = process_pdf_and_create_vectors(
    #                                 file_path, 
    #                                 filename, 
    #                                 openai_key
    #                             )
    #                             all_vectors.extend(vectors)
                    
    #                 # Store vectors in MongoDB
    #                 if all_vectors:
    #                     vectors_collection = db['vectors']
    #                     vectors_collection.create_index([("vector", "2dsphere")])
    #                     vectors_collection.insert_many(all_vectors)
    #                     st.success(f"Created and stored {len(all_vectors)} vectors from the uploaded documents!")
                    
    #                 # Create or update corpus document in MongoDB
    #                 corpus_doc = {
    #                     'username': username,
    #                     'corpus_name': corpus_name,
    #                     'files': saved_files,
    #                     'created_at': datetime.now(),
    #                     'updated_at': datetime.now()
    #                 }
                    
    #                 # Check if corpus already exists for this user
    #                 existing_corpus = corpus_collection.find_one({
    #                     'username': username,
    #                     'corpus_name': corpus_name
    #                 })
                    
    #                 if existing_corpus:
    #                     # Update existing corpus
    #                     corpus_collection.update_one(
    #                         {'_id': existing_corpus['_id']},
    #                         {
    #                             '$set': {
    #                                 'files': list(set(existing_corpus['files'] + saved_files)),
    #                                 'updated_at': datetime.now()
    #                             }
    #                         }
    #                     )
    #                     st.success(f"Files added to existing corpus '{corpus_name}'!")
    #                 else:
    #                     # Create new corpus
    #                     corpus_collection.insert_one(corpus_doc)
    #                     st.success(f"New corpus '{corpus_name}' created successfully!")
                
    #             except Exception as e:
    #                 st.error(f"Error saving corpus: {e}")
    #             # finally:
    #             #     client.close()
            

    #         # columns = st.text_input("Enter the column names for structuring the documents (comma-separated):")

    #         possible_columns = [
    #             "Introduction", "Keywords", "Abstract", "Title", "Methodology", 
    #             "Results", "Conclusion", "Discussion", "Examples", "Policy", 
    #             "Objectives", "Committee", "Programs"
    #         ]

    #         # Let the user select multiple columns
    #         selected_columns = st.multiselect(
    #             "Select the column names for structuring the documents:",
    #             possible_columns
    #         )

    #         # Convert the selected columns into a comma-separated string
    #         columns = ", ".join(selected_columns)

    #         if columns and st.button("Structure Documents"):
    #             try:
    #                 # columns_list = [col.strip() for col in columns.split(',')]
    #                 # columns = st.text_input("Enter the column names for structuring the documents (comma-separated):")
    #                 columns_list = columns
    #                 structured_data = []
                    
    #                 with st.spinner("Structuring documents... This may take a while."):
    #                     for uploaded_file in uploaded_files:
    #                         # Read the document content
    #                         safe_corpus_name = "".join(c for c in corpus_name if c.isalnum() or c in (' ', '-', '_')).strip()
    #                         filename = f"{safe_corpus_name}_{uploaded_file.name}"
    #                         file_path = os.path.join(UPLOAD_DIR, filename)
                            
    #                         document_content = read_pdf_content(file_path)
    #                         if document_content:
    #                             # Structure the content for this document
    #                             row_data = structure_document_content(openai_key, document_content, columns_list)
    #                             if row_data:
    #                                 row_data['filename'] = filename  # Add filename to identify the source
    #                                 structured_data.append(row_data)
                    
    #                 if structured_data:
    #                     # Create DataFrame
    #                     df = pd.DataFrame(structured_data)
    #                     st.write("Structured Document Data:")
    #                     st.dataframe(df)
                        
    #                     # Update corpus document in MongoDB with structured data
    #                     corpus_collection.update_one(
    #                         {
    #                             'username': username,
    #                             'corpus_name': corpus_name
    #                         },
    #                         {
    #                             '$set': {
    #                                 'structured_data': structured_data,
    #                                 'columns': columns_list,
    #                                 'updated_at': datetime.now()
    #                             }
    #                         }
    #                     )
                        
    #                     st.success("Documents structured and stored successfully!")
                        
    #             except Exception as e:
    #                 st.error(f"Error structuring documents: {e}")
                # finally:
                    # client.close()
    with tab2:
        st.subheader("Document Theme Generation")
        st.info("""
        **Document Theme Generation Guidelines**

        - **File Format**: Please upload your documents in **PDF format** for text parsing. If your documents are in Excel or other formats, kindly convert them to PDF before uploading.
        - **Content Quality**: Ensure that your PDFs contain selectable text for accurate text extraction.
        - **Naming Convention**: Use descriptive file names to help organize your corpus effectively.
        """)
        
        # Theme name input
        theme_name = st.text_input("Enter a theme name:", key="theme_name_pdf")

        # PDF file uploader
        uploaded_file = st.file_uploader(
            "Upload a PDF file", 
            type=["pdf"],
            accept_multiple_files=False
        )

        if theme_name and uploaded_file:
            if openai_key:
                try:
                    # Save the uploaded PDF to a temporary location
                    temp_pdf_path = os.path.join(UPLOAD_DIR, uploaded_file.name)
                    # if not os.path.exists("temp"):
                    #     os.makedirs("temp")
                    with open(temp_pdf_path, "wb") as f:
                        f.write(uploaded_file.getbuffer())
                    
                    document_text = read_pdf_content(temp_pdf_path)

                    if document_text:
                        # Define the columns for structuring
                        # columns = "Goals, Description, Keywords, Examples, Reference Links"
                        possible_columns = [
                            "Introduction", "Keywords", "Abstract", "Title", "Methodology", 
                            "Results", "Conclusion", "Discussion", "Examples", "Policy", 
                            "Objectives", "Committee", "Programs", "Goals", "Description",
                            "Keywords", "Examples", "Reference Links"
                        ]

                        # Let the user select multiple columns
                        selected_columns = st.multiselect(
                            "Select the column names for structuring the documents:",
                            possible_columns
                        )

                        # Convert the selected columns into a comma-separated string
                        columns = ", ".join(selected_columns)
                        model = st.selectbox("Select a model for analysis", ["GPT-4o", "Gemini"])

                        # Structure the content using OpenAI API
                        if st.button("Structure this Document Content"):

                            if model == "Gemini":
                                structured_data = structure_data(gemini_key, document_text, columns, model)
                            else:
                                structured_data = structure_data(openai_key, document_text, columns, model)

                            if structured_data:
                                # Display the structured data
                                st.write("**Structured Theme Data:**")

                                df = pd.DataFrame(structured_data)
                                st.dataframe(df)
                                
                                # Store theme in MongoDB
                                theme_doc = {
                                    'username': username,
                                    'theme_title': theme_name,
                                    'structured_data': structured_data,
                                    'timestamp': datetime.now()
                                }
                                themes_collection.insert_one(theme_doc)
                                
                                st.success("Theme generated and saved successfully.")
                            else:
                                st.error("Failed to structure document content.")
                    else:
                        st.error("No text extracted from the PDF. Ensure the PDF contains selectable text.")
                    
                    # Clean up temporary file
                    os.remove(temp_pdf_path)
                except Exception as e:
                    st.error(f"An error occurred: {e}")
            else:
                st.warning("Please set your OpenAI API key in your profile settings.")
    # with tab4:
    #     st.info("Upload an Excel (.xlsx) file for extrapolation analysis. This module analyzes columns of a table, extrapolates the data for new insights and structures the data into a new excel file.")

        # ## select a theme from the available themes

        # themes = themes_collection.find({'username': username})
        # theme_list = [theme['theme_title'] for theme in themes]

        # selected_theme = st.selectbox("Select a theme for analysis", theme_list)

        # ## get the structured table from the selected theme

        # theme_data = themes_collection.find_one({'username': username, 'theme_title': selected_theme})
        # if theme_data:
        #     structured_data = theme_data.get('structured_data', [])
        #     columns = theme_data.get('columns', [])
        #     st.write(f"Structured Data for Theme '{selected_theme}':")
        #     df = pd.DataFrame(structured_data)
        #     ## add a column called ID and set it as the index
        #     df['ID'] = df.index
        #     st.dataframe(df)

        #     ## dropdown for model selection - GPT, Llama, Mistral

        #     model = st.selectbox("Select a model for analysis", ["GPT-4o", "Llama", "Mistral", "Gemini"])

        #     ## if model is llama or mistral add approved huggingface key

        #     if model in ["Llama", "Mistral"]:
        #         huggingface_key = st.text_input("Enter Huggingface API key:")
        #     else:
        #         huggingface_key = None

        #     st.markdown("""
        #     ### Required File Formats - Abstract File:

        #     - Excel file (.xlsx) with column:
        #         1. Abstract (containing research abstracts to analyze)
        #     """)
        #     abstracts_file = st.file_uploader("Upload Excel file with abstracts", type=['xlsx'])
        #     if abstracts_file:
        #         df_abstracts = pd.read_excel(abstracts_file)

        #         abstracts_file_columns = df_abstracts.columns

        #         st.dataframe(df_abstracts)

        #     ## show all columns checkbox to select columns for concatination

        #         selected_columns = st.multiselect("Select columns for analysis", abstracts_file_columns)

        #         df_abstracts["Combined"] = df_abstracts[selected_columns].apply(lambda x: ' '.join(x.dropna().astype(str)), axis=1)

        #     # st.dataframe(df_abstracts)

        #     if abstracts_file is not None:
        #         if model == "Gemini":
        #             main.main(df, df_abstracts, gemini_key, model, huggingface_key)
        #         else:
        #             main.main(df, df_abstracts, openai_key, model, huggingface_key)