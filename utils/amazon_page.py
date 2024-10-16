import streamlit as st
import os
from modules import amazon_reviews
import zipfile
import io

def amazon_page_loader(apify_api_key, op_path):
    num_reviews = st.number_input("Number of reviews", min_value=5, value=5)
    link = st.text_input(f"Amazon Product URL: ")
    links = []
    links.append(link)
    
    if st.button("Analyze"):
        df, amazon_file_name = amazon_reviews.run(apify_api_key, links, op_path, num_reviews)
        st.write("Amazon product reviews details.")
        st.dataframe(df)
        amazon_file_name = os.path.join(op_path, amazon_file_name)
        with open(amazon_file_name, "rb") as f:
            st.download_button(
                label="Download Data",
                data=f,
                file_name=amazon_file_name,
                mime="application/xlsx"
            )