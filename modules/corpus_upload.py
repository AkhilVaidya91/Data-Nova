import streamlit as st
import os
from pymongo import MongoClient

MONGO_URI = "mongodb+srv://akhilvaidya22:qN2dxc1cpwD64TeI@digital-nova.cbbsn.mongodb.net/?retryWrites=true&w=majority&appName=digital-nova"

client = MongoClient(MONGO_URI)
db = client['digital_nova']
corpus_collection = db['corpus']

CHUNK_SIZE = 1000 #characters

def corpus_page(username, model, api_key):
    """Page to handle corpus upload and preprocessing."""
    st.subheader("PDF Corpus Upload")
    st.info("Upload a set of PDF documents for analysis.")

    # Corpus name input
    corpus_name = st.text_input("Enter Corpus Name")

    # File uploader
    uploaded_files = st.file_uploader("Upload PDF Files", type=["pdf"], accept_multiple_files=True)

    if uploaded_files and corpus_name:
        from PyPDF2 import PdfReader

        st.write("Processing uploaded files...")
        extracted_text = {}
        
        for file in uploaded_files:
            try:
                reader = PdfReader(file)
                text = " ".join(page.extract_text() for page in reader.pages)
                extracted_text[file.name] = text
            except Exception as e:
                st.warning(f"Failed to process {file.name}: {e}")

        # Display summary
        st.write("Extraction Summary:")
        st.json({name: len(text) for name, text in extracted_text.items()})

        # Preprocess and vectorize
        if st.button("Preprocess and Save Corpus"):
            from modules.utils import preprocess_text
            from modules.models import LLMModelInterface

            llm_interface = LLMModelInterface()

            file_contents = []
            for name, text in extracted_text.items():
                # preprocessed = preprocess_text(text)
                preprocessed = text

                ## remove whitespace
                preprocessed = preprocessed.replace("\n", " ")
                preprocessed = preprocessed.replace("\t", " ")

                while "  " in preprocessed:
                    preprocessed = preprocessed.replace("  ", " ")
                preprocessed = preprocessed.strip()

                processed_data = []
                for i in range(0, len(preprocessed), CHUNK_SIZE):
                    chunk = preprocessed[i:i+CHUNK_SIZE]
                    if model == "OpenAI":
                        vector = llm_interface.embed_openai(chunk, api_key)
                        # pass
                    elif model == "Gemini":
                        vector = llm_interface.embed_gemini(chunk, api_key)

                    elif model == "USE":
                        vector = llm_interface.embed_use(chunk)

                    elif model == "MiniLM - distilBERT":
                        vector = llm_interface.embed_distilBERT(chunk)

                    # vector = [1, 2, 3] # Placeholder for real vector
                    processed_data.append({"text": chunk, "vector": vector})

                file_content = {
                    "filename": name,
                    "preprocessed_data": processed_data,
                    "processed_data": processed_data,
                    "model": model
                }
                file_contents.append(file_content)

            corpus = {
                "username": username,
                "corpus_name": corpus_name,
                "files": file_contents
            }
            st.json(corpus)

            # Save to MongoDB (placeholder for db_handler integration)
            # st.json(corpus)


            try:
                corpus_collection.insert_one(corpus)
                st.success("Corpus processed and saved successfully.")
            except Exception as e:
                st.error(f"Error processing file: {e}")
                
            st.success("Corpus processed and saved successfully.")