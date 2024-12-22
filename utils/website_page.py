import streamlit as st
from modules.scrape import (
    scrape_website,
    extract_body_content,
    clean_body_content,
    split_dom_content,
)
from modules.parse import parse_with_openai
import pandas as pd
# import markdown
from io import StringIO
from modules import parse, scrape
from pymongo import MongoClient
import json
import os

MONGO_URI = os.getenv('MONGO_URI')
MONGO_URI = "mongodb+srv://akhilvaidya22:qN2dxc1cpwD64TeI@digital-nova.cbbsn.mongodb.net/?retryWrites=true&w=majority&appName=digital-nova"


def markdown_to_dataframe(markdown_content):
    # Extract the table portion of the markdown
    lines = markdown_content.strip().split("\n")
    
    # Remove the separator line (e.g., '|----|----|')
    if len(lines) > 2 and all(c in '-| ' for c in lines[1]):
        lines.pop(1)
    
    # Convert Markdown table to CSV format by replacing '|' with commas
    csv_content = "\n".join([line.replace('|', ',').strip(',') for line in lines])
    
    # Use StringIO to treat the CSV-like string as a file for pandas
    df = pd.read_csv(StringIO(csv_content))
    
    return df

# Streamlit UI
# st.title("AI Web Scraper")
def website_page_loader(username):
    client = MongoClient(MONGO_URI)
    db = client['digital_nova']
    user = db['users']
    current_user = user.find_one({'username': username})
    if current_user:
        api_keys = current_user.get('api_keys', {})
        openai_key = api_keys.get('openai', "")
    else:
        api_keys = {}

    if not openai_key:
        st.warning("Please enter your OpenAI API key in the 'API Keys Management' section.")
        return

    name_website = st.text_input("Enter the name of the website", key="website_name")
    url = st.text_input("Enter Website URL", key="website_url")

    # Step 1: Scrape the Website
    if st.button("Scrape Website", key="scrape_website"):
        if url:
            st.write("Scraping the website...", key="scraping_website")

            # Scrape the website
            dom_content = scrape_website(url)
            body_content = extract_body_content(dom_content)
            cleaned_content = clean_body_content(body_content)

            # Store the DOM content in Streamlit session state
            st.session_state.dom_content = cleaned_content


            # Display the DOM content in an expandable text box
            # with st.expander("View DOM Content"):
            #     st.text_area("DOM Content", cleaned_content, height=300)


    # Step 2: Ask Questions About the DOM Content
    if "dom_content" in st.session_state:
        parse_description = st.text_area("Describe what you want to parse", key="parse_description")

        if st.button("Parse Content", key="parse_content"):
            if parse_description:
                st.write("Parsing the content...")

                # Parse the content with Ollama
                dom_chunks = split_dom_content(st.session_state.dom_content)

                df = parse_with_openai(dom_chunks, parse_description, openai_key)

                st.dataframe(df, key="parsed_content")
                # Convert dataframe to JSON
                json_data = df.to_json(orient='records')

                # Store JSON data in MongoDB 'corpus' collection
                client = MongoClient(MONGO_URI)
                db = client['digital_nova']
                corpus_collection = db['corpus']

                structured_records = {'username': username, 'structured_data': json_data, 'corpus_name': name_website}
                # Insert JSON data into 'corpus' collection
                corpus_collection.insert_one(structured_records)

                st.success("Data has been successfully stored in the 'corpus' collection.")
