import streamlit as st
from pymongo import MongoClient
import os
import pandas as pd

# MongoDB setup
MONGO_URI = os.getenv('MONGO_URI')
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

def display_dashboard(username):
    # st.title("User Dashboard")

    # Fetch user information
    user_info = get_user_info(username)
    if user_info:
        st.subheader(f"User Information: {user_info['username']}")
        # st.write(f"Username: {user_info['username']}")
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
                for file in corpus['files']:
                    st.write(file)
    else:
        st.write("No corpuses found.")

    ## Display the user generated themes

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