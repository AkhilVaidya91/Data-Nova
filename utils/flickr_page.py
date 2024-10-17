import streamlit as st
import os
from modules import flickr
import zipfile
import io

def flickr_page_loader(gemini_api_key, apify_api_key, op_path):
    query = st.text_input("Enter the query: ")
    query = [query]
    max_posts = st.number_input("Max Posts", min_value=1, value=5)
    if st.button("Analyze"):
        df, flickr_file_name = flickr.run(apify_api_key, gemini_api_key, query, max_posts, op_path)
        st.write("Flickr details.")
        st.dataframe(df)
        flickr_file_name = os.path.join(op_path, flickr_file_name)
        with open(flickr_file_name, "rb") as f:
            st.download_button(
                label="Download Data",
                data=f,
                file_name=flickr_file_name,
                mime="application/xlsx"
            )