import streamlit as st
import os
from modules import tripadvisor
import zipfile
import io

def tripadvisor_page_loader(gemini_api_key, apify_api_key, op_path, username):
    num_reviews = st.number_input("Number of reviews", min_value=5, value=5)
    link = st.text_input(f"Tripadvisor property URL: ")
    links = []
    links.append(link)
    if st.button("Analyze"):
        df, trip_file_name = tripadvisor.run(gemini_api_key, apify_api_key, links, num_reviews, op_path, username)
        st.write("Tripadvisor reviews details.")
        st.dataframe(df)
        trip_file_name = os.path.join(op_path, trip_file_name)
        with open(trip_file_name, "rb") as f:
            st.download_button(
                label="Download Data",
                data=f,
                file_name=trip_file_name,
                mime="application/xlsx"
            )