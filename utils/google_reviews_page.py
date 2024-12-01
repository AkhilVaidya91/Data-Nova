import streamlit as st
import os
from modules import google_reviews
import zipfile
from gridfs import GridFS
from pymongo import MongoClient
import io
from datetime import datetime

def google_reviews_page_loader(gemini_api_key, apify_api_key, op_path, username):

    st.info(
        """
        **Google Reviews Scraping Platform**
        - This platform collects and organizes data from Google Maps reviews for analysis and insights.
        - It allows users to scrape reviews based on specific links, date ranges, or public accounts.
        - Outputs are saved in structured Excel files and logged in a MongoDB database for easy retrieval.
        """
    )

    link = st.text_input(f"Google Maps link: ", key="google_maps_link")
    start_date = st.date_input("Start Date", key="google_maps_start_date")
    max_reviews = st.number_input("Max Reviews", min_value=1, value=5, key="google_maps_max_reviews")

    if st.button("Analyze", key="google_maps_analyze"):
        MONGO_URI = os.getenv('MONGO_URI')
        MONGO_URI = "mongodb+srv://akhilvaidya22:qN2dxc1cpwD64TeI@digital-nova.cbbsn.mongodb.net/?retryWrites=true&w=majority&appName=digital-nova"

        client = MongoClient(MONGO_URI)
        db = client['digital_nova']  # Use your existing MongoDB connection
        fs = GridFS(db)

        df, google_file_name = google_reviews.run(apify_api_key, gemini_api_key, link, max_reviews, start_date, op_path, username)
        st.write("Google reviews details.", key="google_reviews_details")
        st.dataframe(df, key="google_reviews_df")

        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        file_id = fs.put(
            excel_buffer.getvalue(),
            filename=google_file_name,
            metadata={
                'username': username,
                'file_type': 'Google Reviews',
                'timestamp': datetime.now()
            }
        )

        grid_file = fs.get(file_id)
        file_data = grid_file.read()

        st.download_button(
            label="Download Data",
            data=file_data,
            file_name=google_file_name,
            mime="application/xlsx",
            key="google_reviews_download_button"
        )