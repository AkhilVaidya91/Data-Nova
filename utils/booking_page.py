import streamlit as st
import os
from modules import booking
import zipfile
import io

def booking_page_loader(apify_api_key, op_path):
    num_reviews = st.number_input("Number of reviews", min_value=5, value=5)
    link = st.text_input(f"Booking.com property URL: ")
    links = []
    links.append(link)
    
    if st.button("Analyze"):
        df, booking_file_name = booking.run(apify_api_key, links, num_reviews, op_path)
        st.write("Booking.com property reviews details.")
        st.dataframe(df)
        booking_file_name = os.path.join(op_path, booking_file_name)
        with open(booking_file_name, "rb") as f:
            st.download_button(
                label="Download Data",
                data=f,
                file_name=booking_file_name,
                mime="application/xlsx"
            )