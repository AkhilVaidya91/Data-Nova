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

def structure_data(api_key, generated_text, columns):
    prompt = f"You are given a large amount of data that can be structured into a table with many rows. Structure the following data into a JSON format with columns: {columns}. Data: {generated_text}. Ensure that you only output the data in JSON format without any other text at all, not even backtics `` and the word JSON. Do not include any other information in the output."
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
    The goals colums should contain the main theme goals that can be identified, keywords should list out atleast 8 keywords per goal.
    
    Document content: {document_text}
    Ensure that your response is extremely detailed and covers every single important point from the document. If it has names or dates or project names mentioned, ensure that they are included in the response.
    Return only a list of JSON object with the specified columns as keys and appropriate content as values. Note that this JSON will be passed on to pandas to convert to a dataframe, so create the dataframe accordingly. DO NOT USE THE WORD JSON IN RESPONSE OR EVEN BACKTICS ```. Start and end your response with curley beackets. 
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
    
    tab1, tab2, tab3 = st.tabs(["Theme Generation", "Corpus Upload", "Doc Theme Generation"])

    user = db['users']
    current_user = user.find_one({'username': username})
    if current_user:
        api_keys = current_user.get('api_keys', {})
        openai_key = api_keys.get('openai', "")
        perplexity_key = api_keys.get('perplexity', "")
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
                if st.button("Structure Data"):
                    if columns:
                        structured_data = structure_data(openai_key, st.session_state.perplexity_text, columns)
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
    with tab2:
        st.subheader("Corpus Upload")
        st.info("""
        **Corpus Structuring Guidelines**

        - **File Format**: Please upload your documents in **PDF format** for text parsing. If your documents are in Excel or other formats, kindly convert them to PDF before uploading.
        - **Content Quality**: Ensure that your PDFs contain selectable text for accurate text extraction.
        - **Naming Convention**: Use descriptive file names to help organize your corpus effectively.

        *Note*: Properly structured corpora improve the performance of vector searches and theme analytics.
        """)
        
        # Create uploads directory if it doesn't exist
        UPLOAD_DIR = "uploads"
        if not os.path.exists(UPLOAD_DIR):
            os.makedirs(UPLOAD_DIR)
        
        # Corpus name input
        corpus_name = st.text_input("Enter a name for your corpus:")
        
        # File uploader
        uploaded_files = st.file_uploader(
            "Upload PDF files", 
            type=["pdf"],
            accept_multiple_files=True
        )
        
        if corpus_name and uploaded_files:

            if st.button("Save Corpus"):
                try:
                    # Save files and collect filenames
                    saved_files = []
                    all_vectors = []
                    
                    for uploaded_file in uploaded_files:
                        # Create a filename that includes corpus name for organization
                        safe_corpus_name = "".join(c for c in corpus_name if c.isalnum() or c in (' ', '-', '_')).strip()
                        filename = f"{safe_corpus_name}_{uploaded_file.name}"
                        file_path = os.path.join(UPLOAD_DIR, filename)
                        
                        # Save file to uploads directory
                        with open(file_path, "wb") as f:
                            f.write(uploaded_file.getbuffer())
                        saved_files.append(filename)
                        
                        # Process PDF and create vectors
                        with st.spinner(f"Processing {filename} and creating vectors..."):
                            vectors = process_pdf_and_create_vectors(
                                file_path, 
                                filename, 
                                openai_key
                            )
                            all_vectors.extend(vectors)
                    
                    # Store vectors in MongoDB
                    if all_vectors:
                        vectors_collection = db['vectors']
                        vectors_collection.create_index([("vector", "2dsphere")])
                        vectors_collection.insert_many(all_vectors)
                        st.success(f"Created and stored {len(all_vectors)} vectors from the uploaded documents!")
                    
                    # Create or update corpus document in MongoDB
                    corpus_doc = {
                        'username': username,
                        'corpus_name': corpus_name,
                        'files': saved_files,
                        'created_at': datetime.now(),
                        'updated_at': datetime.now()
                    }
                    
                    # Check if corpus already exists for this user
                    existing_corpus = corpus_collection.find_one({
                        'username': username,
                        'corpus_name': corpus_name
                    })
                    
                    if existing_corpus:
                        # Update existing corpus
                        corpus_collection.update_one(
                            {'_id': existing_corpus['_id']},
                            {
                                '$set': {
                                    'files': list(set(existing_corpus['files'] + saved_files)),
                                    'updated_at': datetime.now()
                                }
                            }
                        )
                        st.success(f"Files added to existing corpus '{corpus_name}'!")
                    else:
                        # Create new corpus
                        corpus_collection.insert_one(corpus_doc)
                        st.success(f"New corpus '{corpus_name}' created successfully!")
                
                except Exception as e:
                    st.error(f"Error saving corpus: {e}")
                # finally:
                #     client.close()

            columns = st.text_input("Enter the column names for structuring the documents (comma-separated):")

            if columns and st.button("Structure Documents"):
                try:
                    # columns_list = [col.strip() for col in columns.split(',')]
                    columns_list = columns
                    structured_data = []
                    
                    with st.spinner("Structuring documents... This may take a while."):
                        for uploaded_file in uploaded_files:
                            # Read the document content
                            safe_corpus_name = "".join(c for c in corpus_name if c.isalnum() or c in (' ', '-', '_')).strip()
                            filename = f"{safe_corpus_name}_{uploaded_file.name}"
                            file_path = os.path.join(UPLOAD_DIR, filename)
                            
                            document_content = read_pdf_content(file_path)
                            if document_content:
                                # Structure the content for this document
                                row_data = structure_document_content(openai_key, document_content, columns_list)
                                if row_data:
                                    row_data['filename'] = filename  # Add filename to identify the source
                                    structured_data.append(row_data)
                    
                    if structured_data:
                        # Create DataFrame
                        df = pd.DataFrame(structured_data)
                        st.write("Structured Document Data:")
                        st.dataframe(df)
                        
                        # Update corpus document in MongoDB with structured data
                        corpus_collection.update_one(
                            {
                                'username': username,
                                'corpus_name': corpus_name
                            },
                            {
                                '$set': {
                                    'structured_data': structured_data,
                                    'columns': columns_list,
                                    'updated_at': datetime.now()
                                }
                            }
                        )
                        
                        st.success("Documents structured and stored successfully!")
                        
                except Exception as e:
                    st.error(f"Error structuring documents: {e}")
                # finally:
                    # client.close()
    with tab3:
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
            print(1)
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
                        columns = "Goals, Description, Keywords, Examples, Reference Links"
                        
                        # Structure the content using OpenAI API
                        structured_data = structure_data(openai_key, document_text, columns)

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