import streamlit as st
from pymongo import MongoClient
from gridfs import GridFS
import os
import pandas as pd
import json

# MongoDB setup
MONGO_URI = os.getenv('MONGO_URI')
MONGO_URI = "mongodb+srv://akhilvaidya22:qN2dxc1cpwD64TeI@digital-nova.cbbsn.mongodb.net/?retryWrites=true&w=majority&appName=digital-nova"

client = MongoClient(MONGO_URI)
db = client['digital_nova']
users_collection = db['users']
output_files_collection = db['output_files']
corpus_collection = db['corpus']
themes_collection = db['themes']
analytics_collection = db['analytics']
synthesis_collection = db['synthesis']
corpus_file_content = db["corpus_file_content"]
fs = GridFS(db)

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
    st.info("""
    To use all features of this application, please provide your API keys for the services below. You can obtain your API keys from the respective service providers:

    - **Apify**: Obtain your API key from the [Apify Console](https://console.apify.com/account/integrations).
    - **OpenAI**: Generate your API key at [OpenAI API Keys](https://platform.openai.com/account/api-keys).
    - **Perplexity**: Visit [Perplexity AI](https://docs.perplexity.ai/guides/getting-started) to get your API key.
    - **Gemini**: Retrieve your API key from your [Gemini account settings](https://aistudio.google.com/app/apikey).
    - **YouTube**: Create an API key via the [Google Cloud Console](https://console.cloud.google.com/apis/credentials).
    """)
    # Define the API services
    api_services = ['apify', 'openai', 'perplexity', 'gemini', 'YouTube']
    
    # Create columns for the API key management section
    cols = st.columns([2, 2])
    
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
    if not user_info:
        st.error("User not found.")
        return

    # Create tabs
    tab1, tab2, tab3, tab4, tab5, tab6, tab7 = st.tabs(["User Info", "API Keys", "Scraped Files", "Uploaded Corpuses", "Themes", "Analytics", "Synthesis"])

    with tab1:
        # User Info
        st.subheader("User Information")
        st.write(f"**Username:** {user_info['username']}")
        # Add more user info if available
        if 'email' in user_info:
            st.write(f"**Email:** {user_info['email']}")
        if 'full_name' in user_info:
            st.write(f"**Full Name:** {user_info['full_name']}")
        if 'role' in user_info:
            st.write(f"**Role:** {user_info['role']}")


    with tab2:
        # API Keys
        display_api_key_section(username, user_info)

    with tab3:
        # Scraped Files
        st.subheader("Scraped Files")
        output_files = get_user_output_files(username)
        if output_files:
            for file in output_files:
                file_name = file['file_name']
                try:
                    grid_file = fs.find_one({"filename": file_name})
                    if grid_file:

                        file_data = grid_file.read()
                        cols = st.columns([2, 2])
                        with cols[0]:
                            st.write(f"**{file_name}**")
                        with cols[1]:
                            st.download_button(
                                label="Download",
                                data=file_data,
                                file_name=file_name,
                                mime='application/octet-stream'
                            )
                    else:
                        st.warning(f"File {file_name} not found in GridFS")
                except Exception as e:
                    st.error(f"Error retrieving file {file_name}: {str(e)}")

        else:
            st.write("No scraped files found.")

    with tab4:
        # Uploaded Corpuses
        st.subheader("Uploaded Corpuses")
        corpuses = get_user_corpuses(username)
        if corpuses:
            for corpus in corpuses:
                with st.expander(corpus['corpus_name']):
                    # Display the list of files
                    st.write("**Files in corpus:**")
                    for file in corpus.get('files', []):
                        # print(1)
                        # print(file)
                        # filename = file.get('filename', 'Unknown')
                        st.write(f"- {file}")
                    
                    # Display structured data if available
                    # if 'structured_data' in corpus:
                    #     st.write("**Structured Data:**")
                    #     try:
                    #         df = pd.DataFrame(corpus['structured_data'])
                    #         st.dataframe(df, use_container_width=True)
                    #     except Exception as e:
                    #         st.error(f"Error displaying structured data: {str(e)}")
                    # else:
                    #     st.info("No structured data available for this corpus.")
        else:
            st.write("No corpuses found.")

    with tab5:
        # Themes
        st.subheader("Generated Themes")
        themes = get_user_themes(username)
        if themes:
            for theme in themes:
                with st.expander(theme['theme_name']):
                    st.write("**Structured Data:**")
                    try:
                        df = pd.DataFrame(json.loads(theme['structured_df']))
                        st.dataframe(df, use_container_width=True)
                    except Exception as e:
                        st.error(f"Error displaying theme data: {str(e)}")
        else:
            st.write("No themes found.")

    with tab6:
        # Analytics
        st.subheader("Analytics")

        # Fetch analytics data for the user
        # theme_analytics_collection = db['theme_analytics']
        analytics_cursor = analytics_collection.find({'Username': username})
        analytics_data = list(analytics_cursor)

        if analytics_data:
            # Group analytics data by 'Analytics Title'
            from collections import defaultdict
            analytics_groups = defaultdict(list)
            for data in analytics_data:
                # analytics_title = data.get('Analytics Title', 'Untitled Analytics')
                theme = data.get('theme', 'Untitled Theme')
                corpus = data.get('corpus', 'Untitled Corpus')
                name = f"{theme} - {corpus}"
                analytics_groups[name].append(data)

            # Iterate over each analytics group
            for title, data_list in analytics_groups.items():
                with st.expander(title):
                    # Convert the list of data into a DataFrame
                    analytics_df = pd.DataFrame(data_list.get('result', []))

                    # Remove the MongoDB '_id' field if present
                    if '_id' in analytics_df.columns:
                        analytics_df.drop(columns=['_id'], inplace=True)

                    # Display the DataFrame
                    st.dataframe(analytics_df, use_container_width=True)

                    # # Provide option to download CSV
                    # csv_data = analytics_df.to_csv(index=False).encode('utf-8')
                    # st.download_button(
                    #     label="Download Analytics as CSV",
                    #     data=csv_data,
                    #     file_name=f"{title.replace(' ', '_')}.csv",
                    #     mime='text/csv',
                    #     key=f"download_{title}"
                    # )
        else:
            st.write("No analytics data found.")

    with tab7:
        # Analytics
        st.subheader("Literature Synthesis")

        # Fetch analytics data for the user
        # theme_analytics_collection = db['theme_analytics']
        synthesis_cursor = synthesis_collection.find({'Username': username})
        synthesis_data = list(synthesis_cursor)

        if synthesis_data:
            # Group analytics data by 'Analytics Title'
            from collections import defaultdict
            synthesis_groups = defaultdict(list)
            for data in synthesis_data:
                # analytics_title = data.get('Analytics Title', 'Untitled Analytics')
                # theme = data.get('theme', 'Untitled Theme')
                name = data.get('synthesis_name', 'Untitled Synthesis')
                # name = f"{theme} - {corpus}"
                synthesis_groups[name].append(data)

            # Iterate over each analytics group
            for title, data_list in synthesis_groups.items():
                with st.expander(title):
                    # Convert the list of data into a DataFrame
                    synthesis_df = pd.DataFrame(data_list.get('structured_data', []))

                    # Remove the MongoDB '_id' field if present
                    if '_id' in synthesis_df.columns:
                        synthesis_df.drop(columns=['_id'], inplace=True)

                    # Display the DataFrame
                    st.dataframe(synthesis_df, use_container_width=True)

            
        else:
            st.write("No synthesis data found.")


def dashboard():
    if 'username' in st.session_state:
        display_dashboard(st.session_state.username)
    else:
        st.warning("Please log in to view the dashboard.")