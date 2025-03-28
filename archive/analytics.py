import os
import pandas as pd
import numpy as np
from numpy.linalg import norm
from pymongo import MongoClient
import openai
from openai import OpenAI
import streamlit as st
from datetime import datetime, timedelta

import plotly.express as px
import plotly.graph_objects as go
from pytrends.request import TrendReq

# MongoDB connection
MONGO_URI = os.getenv('MONGO_URI')
MONGO_URI = "mongodb+srv://akhilvaidya22:qN2dxc1cpwD64TeI@digital-nova.cbbsn.mongodb.net/?retryWrites=true&w=majority&appName=digital-nova"

client = MongoClient(MONGO_URI)
db = client['digital_nova']
themes_collection = db['themes']
corpus_collection = db['corpus']
vectors_collection = db['vectors']  # Reference to 'vectors' collection
users_collection = db['users']

# Function to create embeddings
def create_embeddings(text, openai_api_key):
    client = OpenAI(api_key=openai_api_key)
    response = client.embeddings.create(
        input=text,
        model="text-embedding-3-small"
    )
    return response.data[0].embedding

# Function to calculate cosine similarity
def cosine_similarity(v1, v2):
    v1 = np.array(v1)
    v2 = np.array(v2)
    dot_product = np.dot(v1, v2)
    norm_product = norm(v1) * norm(v2)
    return dot_product / norm_product if norm_product != 0 else 0

def derive_analytics(goal, reference_text, openai_api_key):
    ## drive summarized analytics based on the extracted test with the goal as the theme using openai

    # call openai to summarize the text

    template = f"""Given a text excerpt from a company's annual report, analyze it following these specific guidelines:
    1. Analyze the text as an experienced financial analyst
    2. Structure the output in markdown with two sections:

    **Insights**
    - Provide 2-3 concise sentences describing the companys actions toward the specified goal
    - Base insights strictly on the provided text
    - Ensure that you include information regarding names, locations, dates, and monetary values if mentioned in the text
    - If no relevant information exists, state No Insights Available

    **Keywords**
    - Extract key elements from the text including:
    * Important phrases
    * Names of people or organizations
    * Locations (with project context ONLY, not just locations)
    * Monetary values (with project context ONLY, not just numbers)
    * Project names
    * Significant dates (with project context ONLY, not just dates)
    - Include only keywords present in the source text
    - If there is No Insights Available in the insights output section, then state No Keywords Available

    Rules:
    - Draw conclusions only from the provided text
    - Keep insights focused on the specific goal mentioned
    - Avoid inferring information not explicitly stated
    - Extract keywords verbatim from the source text
    - Do NOT use bullet points or lists, only plain text (even in keywords)
    - Do NOT use headings or sub headings, just a bold text for the Insights key and Keywords key and rest of the text in plain text

    Here is the text excerpt: {reference_text}
    Here is the relevant goal text: {goal}"""

    client = OpenAI(api_key=openai_api_key)
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        # prompt=template,
        messages=[
        {"role": "user", "content": template}
        ],
        max_tokens=1000,
        temperature=0.2,
    )
    return response.choices[0].message.content

# Retrieve theme data
def get_theme_data(username, theme_title):
    theme = themes_collection.find_one({'username': username, 'theme_title': theme_title})
    if theme:
        df = pd.DataFrame(theme['structured_data'])
        return df
    else:
        raise Exception("Theme not found")

# Retrieve corpus data
def get_corpus_data(username, corpus_name):
    corpus = corpus_collection.find_one({'username': username, 'corpus_name': corpus_name})
    if corpus:
        files = corpus.get('files', [])  # List of file names
        documents = []
        for file_name in files:
            # Fetch all chunks for this file from 'vectors' collection
            chunks_cursor = vectors_collection.find({'file_name': file_name}).sort('chunk_index', 1)
            chunks = list(chunks_cursor)
            if not chunks:
                continue  # Skip if no chunks found for this file

            # Extract texts and embeddings of chunks
            chunk_texts = [chunk.get('text', '') for chunk in chunks]
            chunk_embeddings = [chunk.get('vector', []) for chunk in chunks]

            documents.append({
                'file_name': file_name,
                'texts': chunk_texts,
                'embeddings': chunk_embeddings
            })
        return documents
    else:
        raise Exception("Corpus not found")

# Main function to perform comparative analytics
def comparative_analytics(username, theme_title, corpus_name, openai_api_key):
    # Retrieve theme and corpus data
    theme_df = get_theme_data(username, theme_title)
    corpus_documents = get_corpus_data(username, corpus_name)

    # Create embeddings for theme cells
    theme_embeddings = {}
    for idx, row in theme_df.iterrows():
        for col in theme_df.columns:
            cell_text = str(row[col])
            embedding = create_embeddings(cell_text, openai_api_key)
            theme_embeddings[(idx, col)] = {
                'text': cell_text,
                'embedding': embedding
            }

    # Process each document in the corpus
    results = {}
    for doc in corpus_documents:
        doc_name = doc['file_name']
        chunk_texts = doc['texts']
        chunk_embeddings = doc['embeddings']

        # Convert embeddings to numpy arrays
        chunk_embeddings = [np.array(embedding) for embedding in chunk_embeddings]

        doc_results = []
        for key, theme_value in theme_embeddings.items():
            # For each theme cell
            theme_embedding = np.array(theme_value['embedding'])
            # Compute similarity with each chunk
            similarities = [cosine_similarity(theme_embedding, chunk_embedding) for chunk_embedding in chunk_embeddings]

            # Find the chunk with the highest similarity
            max_similarity = max(similarities)
            max_index = similarities.index(max_similarity)
            matching_text = chunk_texts[max_index]

            doc_results.append({
                'Row': key[0],
                'Column': key[1],
                'Original Theme Text': theme_value['text'],
                'Similarity Score': max_similarity,
                'Matching Text': matching_text
            })

        # Create a DataFrame for this document
        doc_df = pd.DataFrame(doc_results)
        # Set 'Row' and 'Column' as index
        doc_df.set_index(['Row', 'Column'], inplace=True)
        # Unstack 'Column' to create columns for each theme column
        comparative_table = doc_df.unstack('Column')

        # Flatten the column MultiIndex
        comparative_table.columns = [' '.join(col).strip() for col in comparative_table.columns.values]
        comparative_table.reset_index(inplace=True)
        theme_text_columns = [col for col in comparative_table.columns if 'Original Theme Text' in col]
        other_columns = [col for col in comparative_table.columns if col not in ['Row'] + theme_text_columns]
        comparative_table = comparative_table[['Row'] + theme_text_columns + other_columns]
        results[doc_name] = comparative_table

    return results

# Streamlit page to display comparative analytics
def analytics_page(username):
    user = users_collection.find_one({'username': username})
    if user:
        openai_api_key = user.get('api_keys', {}).get('openai', '')
        if not openai_api_key:
            st.error("OpenAI API key not found for the user. Please update your API keys in the dashboard.")
            return
    else:
        st.error("User not found")
        return

    # Select theme and corpus
    st.info(
    "This page allows you to analyze and compare multiple corporate reports against specific themes. "
    "Select a theme and a corpus to uncover insights, and similarities."
    )


    tab1, tab2, tab3 = st.tabs(["Document Analytics", "Theme Analytics", "Google Trends"])

    with tab1:
        themes_cursor = themes_collection.find({'username': username})
        theme_options = [theme['theme_title'] for theme in themes_cursor]
        if not theme_options:
            st.warning("No themes found. Please create a theme first.")
            return

        selected_theme = st.selectbox("Select a Theme", theme_options)

        corpuses_cursor = corpus_collection.find({'username': username})
        corpus_options = [corpus['corpus_name'] for corpus in corpuses_cursor]
        if not corpus_options:
            st.warning("No corpuses found. Please upload a corpus first.")
            return

        selected_corpus = st.selectbox("Select a Corpus", corpus_options)

        if st.button("Run Comparative Analytics"):
            with st.spinner("Running comparative analytics... This may take a few minutes."):
                try:
                    results = comparative_analytics(username, selected_theme, selected_corpus, openai_api_key)
                    st.success("Comparative analytics completed!")
                    # Display results
                    for doc_name, table in results.items():
                        st.info(f"**Comparative Table for Document**: {doc_name}")
                        st.dataframe(table.fillna(''), use_container_width=True)
                except Exception as e:
                    st.error(f"An error occurred: {str(e)}")
    with tab2:
        themes_cursor = themes_collection.find({'username': username})
        theme_options = [theme['theme_title'] for theme in themes_cursor]
        if not theme_options:
            st.warning("No themes found. Please create a theme first.", key="no_themes")
            return

        selected_theme = st.selectbox("Theme Selection", theme_options)

        corpuses_cursor = corpus_collection.find({'username': username})
        corpus_options = [corpus['corpus_name'] for corpus in corpuses_cursor]
        if not corpus_options:
            st.warning("No corpuses found. Please upload a corpus first.")
            return

        selected_corpus = st.selectbox("Corpus Selection", corpus_options)

        analytics_title = st.text_input("Enter the title for the analytics", value=f"{selected_theme} Analytics")

        if st.button("Run Theme Comparative Analytics"):
            theme_df = get_theme_data(username, selected_theme)
            corpus_documents = get_corpus_data(username, selected_corpus)

            analytics_data = []

            for idx, row in theme_df.iterrows():
                goal = row['Goals']
                description = row['Description']
                # keywords = row['Keywords']

                desc_embedding = create_embeddings(description, openai_api_key)
                # keywords_embedding = create_embeddings(keywords, openai_api_key)

                with st.expander(goal):
                            # st.write(row)
                            for doc in corpus_documents:
                                doc_name = doc['file_name']
                                chunk_texts = doc['texts']
                                chunk_embeddings = [np.array(embedding) for embedding in doc['embeddings']]

                                # Compute similarities with Description
                                desc_similarities = [cosine_similarity(desc_embedding, chunk_embedding) for chunk_embedding in chunk_embeddings]
                                max_desc_similarity = max(desc_similarities)
                                max_desc_index = desc_similarities.index(max_desc_similarity)
                                matching_desc_text = chunk_texts[max_desc_index]

                                # Compute similarities with Keywords
                                # keywords_similarities = [cosine_similarity(keywords_embedding, chunk_embedding) for chunk_embedding in chunk_embeddings]
                                # max_keywords_similarity = max(keywords_similarities)
                                # max_keywords_index = keywords_similarities.index(max_keywords_similarity)
                                # matching_keywords_text = chunk_texts[max_keywords_index]

                                st.info(f"**Document:** {doc_name}")
                                relevant_goal = goal
                                relevant_text = matching_desc_text

                                analytics_output = derive_analytics(relevant_goal, relevant_text, openai_api_key)

                                analytics_entry = {
                                    'Username': username,
                                    'Analytics Title': analytics_title,
                                    'Theme Title': selected_theme,
                                    'Corpus Name': selected_corpus,
                                    'Goals': goal,
                                    'Document Name': doc_name,
                                    'Similarity Score': max_desc_similarity,
                                    'Matching Text': matching_desc_text,
                                    'Analytics Output': analytics_output,
                                    'Timestamp': datetime.now()
                                }
                                analytics_data.append(analytics_entry)
                                st.markdown(analytics_output)
                                st.write(f"**Mathing Description text**: {matching_desc_text}")
                                # st.write(f"**Similarity Score with Description**: {max_desc_similarity}")
                
            ##
            if analytics_data:
                theme_analytics_collection = db['theme_analytics']
                theme_analytics_collection.insert_many(analytics_data)
                st.success("Analytics data has been stored in the 'theme_analytics' collection.")

                # Convert analytics data to pandas DataFrame
                analytics_df = pd.DataFrame(analytics_data)

                # Display the DataFrame
                st.dataframe(analytics_df, use_container_width=True)

                # Provide option to download CSV
                csv = analytics_df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    label="Download Analytics as CSV",
                    data=csv,
                    file_name=f"{analytics_title.replace(' ', '_')}.csv",
                    mime='text/csv',
                )
            else:
                st.warning("No analytics data was generated.")
    with tab3:
        pass
        ## take in the user input parameters for google trend analytics as per the ones mentioned in the trends.py file
        ## show the trend graphs then the table and an option to download the data

        ## once the table is generated, store it in mongo db and show the data in the themes collection - with the username, title of the google trends data (all the camma separated keywords in search), the structured data, and the timestamp

        # Create three columns for input parameters
        st.subheader("Search Parameters")
        col1, col2, col3 = st.columns(3)

        with col1:
            # Keywords input
            keywords_input = st.text_input(
                "Enter up to 5 keywords (comma-separated)",
                "Python, JavaScript"
            )

            # Category selection
            categories = {
                "All Categories": 0,
                "Business": 12,
                "Entertainment": 3,
                "Health": 45,
                "Science": 8,
                "Sports": 20,
                "Technology": 5
            }
            selected_category = st.selectbox("Select Category", list(categories.keys()))

        with col2:
            # Time range options
            time_options = {
                "Past Hour": "now 1-H",
                "Past 4 Hours": "now 4-H",
                "Past Day": "now 1-d",
                "Past 7 Days": "now 7-d",
                "Past Month": "today 1-m",
                "Past 3 Months": "today 3-m",
                "Past 12 Months": "today 12-m",
                "Past 5 Years": "today 5-y",
                "Custom Range": "custom"
            }
            selected_timeframe = st.selectbox("Select Time Range", list(time_options.keys()))
            
            # Region selection
            geo_options = {
                "Worldwide": "",
                "United States": "US",
                "United Kingdom": "GB",
                "India": "IN",
                "Canada": "CA",
                "Australia": "AU"
            }
            selected_geo = st.selectbox("Select Region", list(geo_options.keys()))

        with col3:
            # Custom date range if selected
            if selected_timeframe == "Custom Range":
                start_date = st.date_input(
                    "Start Date",
                    datetime.now() - timedelta(days=365)
                )
                end_date = st.date_input(
                    "End Date",
                    datetime.now()
                )
                timeframe = f"{start_date} {end_date}"
            else:
                timeframe = time_options[selected_timeframe]

        # Center the analyze button
        col1, col2, col3 = st.columns([1, 1, 1])
        with col2:
            analyze_button = st.button("Analyze Trends", use_container_width=True)

        # Add a divider
        st.divider()

        # Process inputs when user clicks the button
        if analyze_button:
            try:
                # Clean and validate keywords
                keywords = [k.strip() for k in keywords_input.split(",")]
                if len(keywords) > 5:
                    st.error("Please enter no more than 5 keywords.")
                else:
                    # Ensure pytrends is in session state
                    if 'pytrends' not in st.session_state:
                        st.session_state.pytrends = TrendReq(hl='en-US', tz=360)

                    # Build payload
                    st.session_state.pytrends.build_payload(
                        keywords,
                        cat=categories[selected_category],
                        timeframe=timeframe,
                        geo=geo_options[selected_geo]
                    )
                    
                    # Get interest over time data
                    interest_df = st.session_state.pytrends.interest_over_time()
                    
                    if not interest_df.empty:
                        # Interest Over Time Section
                        st.subheader("Interest Over Time")
                        
                        # Create line chart
                        fig = px.line(
                            interest_df,
                            x=interest_df.index,
                            y=keywords,
                            title="Search Interest Over Time",
                            labels={"value": "Search Interest", "variable": "Keyword"}
                        )
                        fig.update_layout(
                            height=500,
                            margin=dict(t=30, b=0, l=0, r=0)
                        )
                        st.plotly_chart(fig, use_container_width=True)
                        
                        # Add a divider
                        st.divider()
                        
                        # Raw Data Section
                        st.subheader("Raw Data")
                        st.dataframe(interest_df, use_container_width=True)
                        
                        # Download section with some styling
                        st.divider()
                        col1, col2, col3 = st.columns([1, 1, 1])
                        with col2:
                            st.download_button(
                                label="Download Data as CSV",
                                data=interest_df.to_csv().encode('utf-8'),
                                file_name='google_trends_data.csv',
                                mime='text/csv',
                                use_container_width=True
                            )

                        # Store the data in MongoDB

                        # Create a structured data dictionary
                        interest_df.index = interest_df.index.map(str)
                        structured_data = {
                            "Keywords": keywords_input,
                            "Timeframe": timeframe,
                            "Region": selected_geo,
                            "structured_data": interest_df.to_dict(), ## one of the columns has date object giving the error
                            "username": username,
                            "corpus_name": keywords_input,
                            'timestamp': datetime.now()
                        }

                        # Insert the structured data into the 'themes' collection

                        corpus_collection.insert_one(structured_data)
                        st.success("Data has been successfully stored in the 'themes' collection.")
                    else:
                        st.info("No interest over time data available for the selected parameters.")
                        
            except Exception as e:
                st.error(f"An error occurred: {str(e)}")