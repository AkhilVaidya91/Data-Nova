import streamlit as st
import os
from modules import booking
import zipfile
import io

def booking_page_loader(apify_api_key, op_path, username):
    num_reviews = st.number_input("Number of reviews", min_value=5, value=5, key="booking_num_reviews")
    link = st.text_input(f"Booking.com property URL: ", key="booking_link")
    links = []
    links.append(link)
    
    if st.button("Analyze", key="booking_analyze"):
        df, booking_file_name = booking.run(apify_api_key, links, num_reviews, op_path, username)
        st.write("Booking.com property reviews details.", key="booking_reviews_details")
        st.dataframe(df, key="booking_reviews_df")
        booking_file_name = os.path.join(op_path, booking_file_name)
        with open(booking_file_name, "rb") as f:
            st.download_button(
                label="Download Data",
                data=f,
                file_name=booking_file_name,
                mime="application/xlsx",
                key="booking_download_button"
            )