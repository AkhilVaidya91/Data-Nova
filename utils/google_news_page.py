import streamlit as st
import os
from modules import google_news
import zipfile
from gridfs import GridFS
from pymongo import MongoClient
import io
from datetime import datetime

def google_news_page_loader(apify_api_key, gemini_api_key, perplexity_api_key, op_path, username):
    st.info("""
    **About the Scraping Platform**

    This platform is designed for data mining from multiple sources, focusing on **Google News scraping**. It allows users to extract headlines, article content, publication details, and even generate descriptive captions for associated images.

    Please enable the **Google News Scraper Actor** (`lhotanova/google-news-scraper`) on your **Apify Console**.
    Uses Gemini API for image captioning and Perplexity AI for content extraction.

    The data is stored in MongoDB and optionally exported as Excel files for further analysis.
    """)

    query = st.text_input("Enter the query: ", key="google_news_query")
    start_date = st.date_input('Enter the start date (older date)', key="google_news_start_date")
    end_date = st.date_input('Enter the end date (new date)', key="google_news_end_date")
    max_articles = st.number_input('Max news articles', min_value=2, value=5, key="google_news_max_articles")
    if st.button("Analyze", key="google_news_analyze"):
        MONGO_URI = os.getenv('MONGO_URI')
        MONGO_URI = "mongodb+srv://akhilvaidya22:qN2dxc1cpwD64TeI@digital-nova.cbbsn.mongodb.net/?retryWrites=true&w=majority&appName=digital-nova"

        client = MongoClient(MONGO_URI)
        db = client['digital_nova']  # Use your existing MongoDB connection
        fs = GridFS(db)

        df, google_file_name = google_news.run(apify_api_key, gemini_api_key, perplexity_api_key, query, max_articles, start_date, end_date, op_path, username)
        st.write("Google News details.", key="google_news_details")
        st.dataframe(df, key="google_news_df")

        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        file_id = fs.put(
            excel_buffer.getvalue(),
            filename=google_file_name,
            metadata={
                'username': username,
                'file_type': 'Google News',
                'timestamp': datetime.now()
            }
        )

        grid_file = fs.get(file_id)
        file_data = grid_file.read()

        # google_file_name = os.path.join(op_path, google_file_name)
        # with open(google_file_name, "rb") as f:
        st.download_button(
            label="Download Data",
            data=file_data,
            file_name=google_file_name,
            mime="application/xlsx",
            key="google_news_download_button"
        )