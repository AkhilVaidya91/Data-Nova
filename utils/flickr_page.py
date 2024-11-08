import streamlit as st
import os
from modules import flickr
import zipfile
from gridfs import GridFS
from pymongo import MongoClient
import io
from datetime import datetime

def flickr_page_loader(gemini_api_key, apify_api_key, op_path, username):
    MONGO_URI = os.getenv('MONGO_URI')
    MONGO_URI = "mongodb+srv://akhilvaidya22:qN2dxc1cpwD64TeI@digital-nova.cbbsn.mongodb.net/?retryWrites=true&w=majority&appName=digital-nova"

    client = MongoClient(MONGO_URI)
    db = client['digital_nova']  # Use your existing MongoDB connection
    fs = GridFS(db)

    query = st.text_input("Enter the query: ", key="flickr_query")
    query = [query]
    max_posts = st.number_input("Max Posts", min_value=1, value=5, key="flickr_max_posts")
    if st.button("Analyze", key="flickr_analyze"):
        df, flickr_file_name = flickr.run(apify_api_key, gemini_api_key, query, max_posts, op_path, username)
        st.write("Flickr details.", key="flickr_details")
        st.dataframe(df, key="flickr_df")

        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        file_id = fs.put(
            excel_buffer.getvalue(),
            filename=flickr_file_name,
            metadata={
                'username': username,
                'file_type': 'Flickr Data',
                'timestamp': datetime.now()
            }
        )
        grid_file = fs.get(file_id)
        file_data = grid_file.read()

        # flickr_file_name = os.path.join(op_path, flickr_file_name)
        # with open(flickr_file_name, "rb") as f:
        st.download_button(
            label="Download Data",
            data=file_data,
            file_name=flickr_file_name,
            mime="application/xlsx",
            key="flickr_download_button"
        )