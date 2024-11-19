import streamlit as st
import os
from modules import tripadvisor
import zipfile
from gridfs import GridFS
from pymongo import MongoClient
import io
from datetime import datetime

def tripadvisor_page_loader(gemini_api_key, apify_api_key, op_path, username):
    st.info("""
    **TripAdvisor Hotel Reviews Scraping Platform**  
    This platform allows you to scrape hotel reviews and related metadata from TripAdvisor efficiently.  
    - **Purpose**: Extract reviews with details like ratings, dates, reviewer info, helpful votes, captions for attached images (via Gemini API), and location metadata for comprehensive analysis.  
    - **Required Apify Actor**: Enable the actor **`maxcopell/tripadvisor-reviews`** in your Apify Console to fetch review data.   

    """)

    num_reviews = st.number_input("Number of reviews", min_value=5, value=5, key="tripadvisor_num_reviews")
    link = st.text_input(f"Tripadvisor property URL: ", key="tripadvisor_link")
    links = []
    links.append(link)
    if st.button("Analyze", key="tripadvisor_analyze"):
        MONGO_URI = os.getenv('MONGO_URI')
        MONGO_URI = "mongodb+srv://akhilvaidya22:qN2dxc1cpwD64TeI@digital-nova.cbbsn.mongodb.net/?retryWrites=true&w=majority&appName=digital-nova"

        client = MongoClient(MONGO_URI)
        db = client['digital_nova']  # Use your existing MongoDB connection
        fs = GridFS(db)

        df, trip_file_name = tripadvisor.run(gemini_api_key, apify_api_key, links, num_reviews, op_path, username)
        st.write("Tripadvisor reviews details.", key="tripadvisor_reviews_details")
        st.dataframe(df, key="tripadvisor_reviews_df")

        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        file_id = fs.put(
            excel_buffer.getvalue(),
            filename=trip_file_name,
            metadata={
                'username': username,
                'file_type': 'Tripadvisor Reviews',
                'timestamp': datetime.now()
            }
        )

        grid_file = fs.get(file_id)
        file_data = grid_file.read()

        # trip_file_name = os.path.join(op_path, trip_file_name)
        # with open(trip_file_name, "rb") as f:
        st.download_button(
            label="Download Data",
            data=file_data,
            file_name=trip_file_name,
            mime="application/xlsx",
            key="tripadvisor_download_button"
        )