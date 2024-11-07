import streamlit as st
import os
from modules import google_news
import zipfile
import io

def google_news_page_loader(apify_api_key, gemini_api_key, perplexity_api_key, op_path, username):
    query = st.text_input("Enter the query: ", key="google_news_query")
    start_date = st.date_input('Enter the start date (older date)', key="google_news_start_date")
    end_date = st.date_input('Enter the end date (new date)', key="google_news_end_date")
    max_articles = st.number_input('Max news articles', min_value=2, value=5, key="google_news_max_articles")
    if st.button("Analyze", key="google_news_analyze"):
        df, google_file_name = google_news.run(apify_api_key, gemini_api_key, perplexity_api_key, query, max_articles, start_date, end_date, op_path, username)
        st.write("Google News details.", key="google_news_details")
        st.dataframe(df, key="google_news_df")
        google_file_name = os.path.join(op_path, google_file_name)
        with open(google_file_name, "rb") as f:
            st.download_button(
                label="Download Data",
                data=f,
                file_name=google_file_name,
                mime="application/xlsx",
                key="google_news_download_button"
            )