import streamlit as st
from openai import OpenAI
import requests
import json
import pandas as pd

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
            "content": "You are an AI that structures data into JSON format for converting unstructured text data into tables. Ensure that you have atlest as many rows in the output as much mentioned in the input text."
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

# Streamlit app
def themes_main():
    st.title("Perplexity API Data Fetcher")
    
    # Initialize session state variables
    if "perplexity_text" not in st.session_state:
        st.session_state.perplexity_text = ""
    if "generated_text" not in st.session_state:
        st.session_state.generated_text = ""
    if "show_buttons" not in st.session_state:
        st.session_state.show_buttons = False

    perplexity_api_key = st.text_input("Enter your Perplexity API Key:")
    openai_api_key = st.text_input("Enter your OpenAI API Key:")

    if not perplexity_api_key:
        st.warning("Please enter your Perplexity API Key to proceed.")

    if not openai_api_key:
        st.warning("Please enter your OpenAI API Key to proceed.")

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
                        df = pd.DataFrame(structured_data)
                        st.dataframe(df)
                else:
                    st.warning("Please enter columns to structure data.")