import streamlit as st
import os
from modules import google_news
import zipfile
import io

def google_news_page_loader(apify_api_key, gemini_api_key, perplexity_api_key, op_path):
    query = st.text_input("Enter the query: ")
    start_date = st.date_input('Enter the start date (older date)')
    end_date = st.date_input('Enter the end date (new date)')
    max_articles = st.number_input('Max news articles', min_value=2, value=5)
    if st.button("Analyze"):
        df, google_file_name = google_news.run(apify_api_key, gemini_api_key, perplexity_api_key, query, max_articles, start_date, end_date, op_path)
        st.write("Google News details.")
        st.dataframe(df)
        google_file_name = os.path.join(op_path, google_file_name)
        with open(google_file_name, "rb") as f:
            st.download_button(
                label="Download Data",
                data=f,
                file_name=google_file_name,
                mime="application/xlsx"
            )