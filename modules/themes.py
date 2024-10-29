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
                "You are a UN expert providing official information about the Sustainable Development Goals. Provide only verified information with working reference links."
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
    finally:
        client.close()

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
    finally:
        client.close()

# Streamlit app
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

    tab1, tab2 = st.tabs(["Data Generation", "Corpus Upload"])
    
    with tab1:
        perplexity_api_key = st.text_input("Enter your Perplexity API Key:", key="perplexity_key_tab1")
        openai_api_key = st.text_input("Enter your OpenAI API Key:", key="openai_key_tab1")
        mongodb_uri = st.text_input("Enter your MongoDB Atlas URI:", key="mongodb_uri_tab1")

        if not perplexity_api_key:
            st.warning("Please enter your Perplexity API Key to proceed.")
        if not openai_api_key:
            st.warning("Please enter your OpenAI API Key to proceed.")
        if not mongodb_uri:
            st.warning("Please enter your MongoDB Atlas URI to proceed.")

        if perplexity_api_key:
            topic = st.text_input("Enter a topic:")
            
            if st.button("Generate"):
                if topic:
                    st.session_state.generated_text = fetch_perplexity_data(perplexity_api_key, topic)
                    if st.session_state.generated_text:
                        st.markdown(st.session_state.generated_text)
                        st.session_state.show_buttons = True
                else:
                    st.warning("Please enter a topic to generate text.")

            # Show Keep/Discard buttons only after generation
            if st.session_state.show_buttons:
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("Keep"):
                        st.session_state.perplexity_text = st.session_state.generated_text
                        st.success("Text kept successfully!")
                with col2:
                    if st.button("Discard"):
                        st.session_state.generated_text = ""
                        st.session_state.show_buttons = False
                        st.warning("Text discarded. Please enter a new topic.")

            # Show the structuring options only if there's kept text
            if st.session_state.perplexity_text:
                st.subheader("Stored Text")
                st.markdown(st.session_state.perplexity_text)
                
                columns = st.text_input("Enter columns (comma-separated):")
                if st.button("Structure Data"):
                    if columns:
                        structured_data = structure_data(openai_api_key, st.session_state.perplexity_text, columns)
                        if structured_data:
                            st.session_state.dataframe = pd.DataFrame(structured_data)
                            st.dataframe(st.session_state.dataframe)
                            theme_title = generate_theme_title(openai_api_key, st.session_state.perplexity_text)
                            st.session_state.theme_title = theme_title
                        
                        # Store structured table in MongoDB
                        mongo_uri = os.getenv('MONGO_URI')
                        mongo_uri = "mongodb+srv://akhilvaidya22:qN2dxc1cpwD64TeI@digital-nova.cbbsn.mongodb.net/?retryWrites=true&w=majority&appName=digital-nova"
                        database_name = 'digital_nova'
                        client = MongoClient(mongo_uri)
                        db = client[database_name]
                        themes_collection = db['themes']
                        
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
                
                # Add Vector Store Creation Button
                if st.session_state.dataframe is not None:
                    if st.button("Create Vector Store"):
                        try:
                            with st.spinner("Creating vector store... This may take a while depending on the size of your data."):
                                num_vectors = store_vectors_mongodb(
                                    st.session_state.dataframe,
                                    mongodb_uri,
                                    openai_api_key,
                                    st.session_state.theme_title
                                )
                            st.session_state.vector_store_created = True
                            st.success(f"Successfully created vector store with {num_vectors} vectors!")
                        except Exception as e:
                            st.error(f"Failed to create vector store: {e}")
    
    # Vector Search Tab
    with tab2:
        st.subheader("Corpus Upload")