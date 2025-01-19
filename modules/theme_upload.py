import streamlit as st
import json
import os
from pymongo import MongoClient
from datetime import datetime
from openai import OpenAI
from modules.models import LLMModelInterface
import pandas as pd
import PyPDF2


MONGO_URI = "mongodb+srv://akhilvaidya22:qN2dxc1cpwD64TeI@digital-nova.cbbsn.mongodb.net/?retryWrites=true&w=majority&appName=digital-nova"
UPLOAD_DIR = "uploads"
if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR)
client = MongoClient(MONGO_URI)
db = client['digital_nova']
themes_collection = db['themes']

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

def structure_data(api_key, generated_text, columns, model):
    prompt = f"You are an AI that structures data into JSON format (list of python dictionaries) for converting unstructured text data into tables. Ensure that you have atlest as many rows in the output as much mentioned in the input text. Return the data in such a way that it is a list of dictionaried that can be converted to a pandas dataframe directly. You are given a large amount of data that can be structured into a table with many rows. Structure the following data into a list of JSON format with columns: {columns}. Data: {generated_text}. Ensure that you only output the data in JSON format without any other text at all, not even backtics `` and the word JSON. Do not include any other information in the output. Start your output string with an opening square brace [ and end with a closing square brace ] as it's last characcter of the srting (strictly follow this rule). Ensure that the list of JSON/python dictionaries can be directly parsed to a dataframe without any additional text."
    interface = LLMModelInterface()
    # print("Model: ", model)
    if model == "Gemini":
        print("Using Gemini")
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
            model="gpt-4o-mini",
            messages=messages,
            temperature=0.1,
        )
        json_content = response.choices[0].message.content
        return json.loads(json_content)
    except Exception as e:
        st.error(f"Failed to structure data using GPT-4o Mini: {e}")
        return []


def theme_page(username, model, api_key):
    """Page to handle theme upload and processing."""
    st.subheader("Reference Master Theme Upload")
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
                possible_columns = [
                    "Introduction", "Keywords", "Abstract", "Title", "Methodology", 
                    "Results", "Conclusion", "Discussion", "Examples", "Policy", 
                    "Objectives", "Committee", "Programs", "Goals", "Description",
                    "Examples", "Reference Links"
                ]

                # Let the user select multiple columns
                selected_columns = st.multiselect(
                    "Select the column names for structuring the documents:",
                    possible_columns
                )

                # Convert the selected columns into a comma-separated string
                columns = ", ".join(selected_columns)
                # st.info("Columns: Goal, Description, Keywords, Reference links, Examples")
                model_user_ip = st.selectbox("Select a model for analysis", ["GPT-4o", "Gemini"])
                api_key_ip = st.text_input("Enter API Key", key="api_key_pdf_1")

                if st.button("Structure Data"):
                    if columns:
                        if model_user_ip == "Gemini":
                            structured_data = structure_data(api_key_ip, st.session_state.perplexity_text, columns, model_user_ip)
                        elif model_user_ip == "GPT-4o":
                            structured_data = structure_data(api_key_ip, st.session_state.perplexity_text, columns, model_user_ip)
                        if structured_data:
                            st.session_state.dataframe = pd.DataFrame(structured_data)
                            df = pd.DataFrame(structured_data)
                            st.dataframe(st.session_state.dataframe)
                            # theme_title = generate_theme_title(openai_key, st.session_state.perplexity_text)
                            theme_title = st.session_state.current_theme
                            st.session_state.theme_title = theme_title

                            structured_df_json = df.to_json(orient="records")
                            structured_df_json = structured_data
                            # if st.button("Process and Save Theme"):
                                # print("Processing and saving theme...")
                            from modules.models import LLMModelInterface
                                # print(1)
                            llm_interface = LLMModelInterface()

                            columns = df.columns
                            # print(columns)
                            explanations = []
                            for i, row in df.iterrows():
                                explanation = f"T {i+1}:\n"
                                for col in columns:
                                    explanation += f"{col}: {row[col]}\n"
                                explanations.append(explanation.strip())

                            combined_tuples = []

                            for explanation in explanations:
                                if model == "OpenAI":
                                    embedding = llm_interface.embed_openai(explanation, api_key)
                                    
                                elif model == "Gemini":
                                    embedding = llm_interface.embed_gemini(explanation, api_key)
                                
                                elif model == "USE":
                                    embedding = llm_interface.embed_use(explanation)

                                elif model == "MiniLM - distilBERT":
                                    embedding = llm_interface.embed_distilBERT(explanation)

                                # embedding = [1,2,3]
                                dict_ = {"text": explanation, "vector": embedding}
                                combined_tuples.append(dict_)

                            theme = {
                                "username": username,
                                "theme_name": theme_name,
                                "structured_df": structured_df_json,
                                "reference_vectors": combined_tuples,
                                "model": model
                            }


                            # st.json(theme)

                            ## store in MongoDB
                            try:
                                themes_collection.insert_one(theme)
                                st.success("Theme processed and saved successfully.")

                            except Exception as e:
                                st.error(f"Error processing file: {e}")

                            st.success("Theme processed and saved successfully.")

                    
                        
                        # theme_data = {
                        #     'username': username,
                        #     'theme_title': theme_title,
                        #     'structured_data': structured_data,
                        #     'created_at': datetime.now(),
                        #     'updated_at': datetime.now()
                        # }
                        
                        # themes_collection.insert_one(theme_data)
                        # st.success(f"Structured table stored in MongoDB with theme title '{theme_title}' successfully!")
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
                            "Examples", "Reference Links"
                        ]

                        # Let the user select multiple columns
                        selected_columns = st.multiselect(
                            "Select the column names for structuring the documents:",
                            possible_columns
                        )

                        # Convert the selected columns into a comma-separated string
                        columns = ", ".join(selected_columns)
                        model_user_ip_tab_2 = st.selectbox("Select a model for analysis", ["GPT-4o", "Gemini"])
                        api_key_ip_tab_2 = st.text_input("Enter API Key", key="api_key_pdf")

                        # Structure the content using OpenAI API
                        if st.button("Structure this Document Content"):

                            if model_user_ip_tab_2 == "Gemini":
                                structured_data = structure_data(api_key_ip_tab_2, document_text, columns, model_user_ip_tab_2)
                            else:
                                structured_data = structure_data(api_key_ip_tab_2, document_text, columns, model_user_ip_tab_2)

                            if structured_data:
                                # Display the structured data
                                st.write("**Structured Theme Data:**")

                                df = pd.DataFrame(structured_data)
                                st.dataframe(df)
                                structured_df_json = df.to_json(orient="records")

                                st.json(structured_df_json)
                                
                                if st.button("Process and Save Theme"):
                                    from modules.models import LLMModelInterface

                                    llm_interface = LLMModelInterface()

                                    columns = df.columns
                                    explanations = []
                                    for i, row in df.iterrows():
                                        explanation = f"UN SDG {i+1}:\n"
                                        for col in columns:
                                            explanation += f"{col}: {row[col]}\n"
                                        explanations.append(explanation.strip())

                                    combined_tuples = []

                                    for explanation in explanations:
                                        if model == "OpenAI":
                                            embedding = llm_interface.embed_openai(explanation, api_key)
                                            
                                        elif model == "Gemini":
                                            embedding = llm_interface.embed_gemini(explanation, api_key)
                                        
                                        elif model == "USE":
                                            embedding = llm_interface.embed_use(explanation)

                                        elif model == "MiniLM - distilBERT":
                                            embedding = llm_interface.embed_distilBERT(explanation)

                                        # embedding = [1,2,3]
                                        dict_ = {"text": explanation, "vector": embedding}
                                        combined_tuples.append(dict_)

                                    theme = {
                                        "username": username,
                                        "theme_name": theme_name,
                                        "structured_df": structured_df_json,
                                        "reference_vectors": combined_tuples,
                                        "model": model
                                    }

                                    # st.json(theme)

                                    ## store in MongoDB
                                    try:
                                        themes_collection.insert_one(theme)
                                        st.success("Theme processed and saved successfully.")

                                    except Exception as e:
                                        st.error(f"Error processing file: {e}")

                                    st.success("Theme processed and saved successfully.")

                except Exception as e:
                    st.error(f"Error processing file: {e}")


    # # theme_name = st.text_input("Enter Theme Name")

    # # File upload
    # uploaded_file = st.file_uploader("Upload Excel File", type=["xlsx"])

    # if uploaded_file:
    #     import pandas as pd

    #     # Load and display file
    #     try:
    #         df = pd.read_excel(uploaded_file)
    #         st.write("Uploaded Data:")
    #         st.dataframe(df)

    #         structured_df_json = df.to_json(orient="records")

    #         st.json(structured_df_json)
            
    #         if st.button("Process and Save Theme"):
    #             from modules.models import LLMModelInterface

    #             llm_interface = LLMModelInterface()

    #             columns = df.columns
    #             explanations = []
    #             for i, row in df.iterrows():
    #                 explanation = f"UN SDG {i+1}:\n"
    #                 for col in columns:
    #                     explanation += f"{col}: {row[col]}\n"
    #                 explanations.append(explanation.strip())

    #             combined_tuples = []

    #             for explanation in explanations:
    #                 if model == "OpenAI":
    #                     embedding = llm_interface.embed_openai(explanation, api_key)
                        
    #                 elif model == "Gemini":
    #                     embedding = llm_interface.embed_gemini(explanation, api_key)
                    
    #                 elif model == "USE":
    #                     embedding = llm_interface.embed_use(explanation)

    #                 elif model == "MiniLM - distilBERT":
    #                     embedding = llm_interface.embed_distilBERT(explanation)

    #                 # embedding = [1,2,3]
    #                 dict_ = {"text": explanation, "vector": embedding}
    #                 combined_tuples.append(dict_)

    #             theme = {
    #                 "username": username,
    #                 "theme_name": theme_name,
    #                 "structured_df": structured_df_json,
    #                 "reference_vectors": combined_tuples,
    #                 "model": model
    #             }

    #             # st.json(theme)

    #             ## store in MongoDB
    #             try:
    #                 themes_collection.insert_one(theme)
    #                 st.success("Theme processed and saved successfully.")

    #             except Exception as e:
    #                 st.error(f"Error processing file: {e}")

    #             st.success("Theme processed and saved successfully.")

    #     except Exception as e:
    #         st.error(f"Error processing file: {e}")