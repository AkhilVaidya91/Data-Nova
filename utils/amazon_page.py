import streamlit as st
import os
from modules import amazon_reviews
import zipfile
from gridfs import GridFS
from pymongo import MongoClient
import io
from datetime import datetime

def amazon_page_loader(apify_api_key, op_path, username):
    MONGO_URI = os.getenv('MONGO_URI')
    MONGO_URI = "mongodb+srv://akhilvaidya22:qN2dxc1cpwD64TeI@digital-nova.cbbsn.mongodb.net/?retryWrites=true&w=majority&appName=digital-nova"

    client = MongoClient(MONGO_URI)
    db = client['digital_nova']  # Use your existing MongoDB connection
    fs = GridFS(db)
    st.info("""
    **Amazon Reviews Scraper Platform**

    This platform is designed to scrape **Amazon product reviews** using the **Junglee/Amazon Reviews Scraper** actor from Apify. The tool extracts review details such as rating, title, reactions, country, date, description, and product variant, and organizes them into an Excel file. 

    **Prerequisites:**
    1. **Apify API Key**: Generate and provide your Apify API key in the application dashboard.
    2. **Apify Actor**: Ensure the **Junglee/Amazon Reviews Scraper** actor is enabled in your Apify Console.
    """)

    num_reviews = st.number_input("Number of reviews", min_value=5, value=5, key="amazon_num_reviews")
    link = st.text_input(f"Amazon Product URL: ", key="amazon_link")
    links = []
    links.append(link)
    
    if st.button("Analyze", key="amazon_analyze"):
        df, amazon_file_name = amazon_reviews.run(apify_api_key, links, op_path, username, num_reviews)
        st.write("Amazon product reviews details.", key="amazon_reviews_details")
        st.dataframe(df, key="amazon_reviews_df")

        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        file_id = fs.put(
            excel_buffer.getvalue(),
            filename=amazon_file_name,
            metadata={
                'username': username,
                'file_type': 'Amazon Reviews',
                'timestamp': datetime.now()
            }
        )
        # amazon_file_name = os.path.join(op_path, amazon_file_name)
        grid_file = fs.get(file_id)
        file_data = grid_file.read()

        # with open(amazon_file_name, "rb") as f:
        st.download_button(
            label="Download Data",
            data=file_data,
            file_name=amazon_file_name,
            mime="application/xlsx",
            key="amazon_download_button"
        )