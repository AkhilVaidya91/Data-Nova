import streamlit as st
from pymongo import MongoClient
import os
import pandas as pd

# MongoDB setup
MONGO_URI = os.getenv('MONGO_URI')
# MONGO_URI = "mongodb+srv://akhilvaidya22:qN2dxc1cpwD64TeI@digital-nova.cbbsn.mongodb.net/?retryWrites=true&w=majority&appName=digital-nova"

client = MongoClient(MONGO_URI)
db = client['digital_nova']
users_collection = db['users']
output_files_collection = db['output_files']
corpus_collection = db['corpus']
themes_collection = db['themes']

def get_user_info(username):
    user = users_collection.find_one({'username': username})
    return user

def get_user_output_files(username):
    files = output_files_collection.find({'username': username})
    return list(files)

def get_user_corpuses(username):
    corpuses = corpus_collection.find({'username': username})
    return list(corpuses)

def get_user_themes(username):
    themes = themes_collection.find({'username': username})
    return list(themes)

def update_api_key(username, api_name, api_key):
    users_collection.update_one(
        {'username': username},
        {'$set': {f'api_keys.{api_name}': api_key}}
    )

def display_api_key_section(username, user_info):
    st.subheader("API Keys Management")
    
    # Define the API services
    api_services = ['apify', 'openai', 'perplexity', 'gemini', 'YouTube']
    
    # Create columns for the API key management section
    cols = st.columns([2, 1])
    
    with cols[0]:
        # Get existing API keys from user_info
        api_keys = user_info.get('api_keys', {})
        
        for service in api_services:
            st.write(f"\n{service.upper()} API Key")
            if service in api_keys:
                # Show placeholder for existing API key
                st.text("*" * 20 + api_keys[service][-4:])
            else:
                # Show input field for new API key
                new_key = st.text_input(f"Enter {service} API key", 
                                      key=f"new_{service}_key",
                                      label_visibility="collapsed")
                if new_key:
                    update_api_key(username, service, new_key)
                    st.success(f"{service.upper()} API key added successfully!")
                    st.rerun()

    with cols[1]:
        for service in api_services:
            st.write("")  # Add spacing to align with the API key fields
            if service in api_keys:
                if st.button(f"Edit {service.upper()}", key=f"edit_{service}"):
                    # Remove the existing API key to show input field
                    users_collection.update_one(
                        {'username': username},
                        {'$unset': {f'api_keys.{service}': ""}}
                    )
                    st.rerun()

def display_dashboard(username):
    # Fetch user information
    user_info = get_user_info(username)
    if user_info:
        st.subheader(f"User Information: {user_info['username']}")

    # Display API Keys Section
    display_api_key_section(username, user_info)
    
    # Display table of all user's generated output files
    st.subheader("Generated Output Files")
    output_files = get_user_output_files(username)
    if output_files:
        for file in output_files:
            file_path = file['file_path']
            file_name = file['file_name']
            with open(file_path, "rb") as file_data:
                st.write(file_name)
                st.download_button(
                    label="Download",
                    data=file_data,
                    file_name=file_name,
                    mime='application/octet-stream'
                )
    else:
        st.write("No output files found.")

    # Display list of all user-uploaded corpuses
    st.subheader("Uploaded Corpuses")
    corpuses = get_user_corpuses(username)
    if corpuses:
        for corpus in corpuses:
            with st.expander(corpus['corpus_name']):
                # Display the list of files
                st.write("Files in corpus:")
                for file in corpus['files']:
                    st.write(f"- {file}")
                
                # Display structured data if available
                if 'structured_data' in corpus:
                    st.write("\nStructured Data:")
                    try:
                        # Convert structured data to dataframe if it's not already
                        if isinstance(corpus['structured_data'], pd.DataFrame):
                            df = corpus['structured_data']
                        else:
                            df = pd.DataFrame(corpus['structured_data'])
                        
                        # Display the dataframe with styling
                        st.dataframe(
                            df,
                            use_container_width=True,
                            hide_index=True
                        )
                    except Exception as e:
                        st.error(f"Error displaying structured data: {str(e)}")
                else:
                    st.info("No structured data available for this corpus")
    else:
        st.write("No corpuses found.")

    # Display the user generated themes
    st.subheader("Generated Themes")
    themes = get_user_themes(username)
    if themes:
        for theme in themes:
            with st.expander(theme['theme_title']):
                st.dataframe(theme['structured_data'])
    else:
        st.write("No themes found.")

def dashboard():
    if 'username' in st.session_state:
        display_dashboard(st.session_state.username)
    else:
        st.warning("Please log in to view the dashboard.")