import streamlit as st
import os
from modules import booking
import zipfile
from gridfs import GridFS
from pymongo import MongoClient
import io
from datetime import datetime

def booking_page_loader(apify_api_key, op_path, username):
    num_reviews = st.number_input("Number of reviews", min_value=5, value=5, key="booking_num_reviews")
    link = st.text_input(f"Booking.com property URL: ", key="booking_link")
    links = []
    links.append(link)
    
    if st.button("Analyze", key="booking_analyze"):
        MONGO_URI = os.getenv('MONGO_URI')
        MONGO_URI = "mongodb+srv://akhilvaidya22:qN2dxc1cpwD64TeI@digital-nova.cbbsn.mongodb.net/?retryWrites=true&w=majority&appName=digital-nova"

        client = MongoClient(MONGO_URI)
        db = client['digital_nova']  # Use your existing MongoDB connection
        fs = GridFS(db)
        df, booking_file_name = booking.run(apify_api_key, links, num_reviews, op_path, username)
        st.write("Booking.com property reviews details.", key="booking_reviews_details")
        st.dataframe(df, key="booking_reviews_df")

        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        file_id = fs.put(
            excel_buffer.getvalue(),
            filename=booking_file_name,
            metadata={
                'username': username,
                'file_type': 'Booking.com Reviews',
                'timestamp': datetime.now()
            }
        )

        # booking_file_name = os.path.join(op_path, booking_file_name)

        grid_file = fs.get(file_id)
        file_data = grid_file.read()
        # with open(booking_file_name, "rb") as f:
        st.download_button(
            label="Download Data",
            # data=f,
            data=file_data,
            file_name=booking_file_name,
            mime="application/xlsx",
            key="booking_download_button"
        )