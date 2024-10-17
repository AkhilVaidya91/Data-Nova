import streamlit as st
import os
from modules import twitter
import zipfile
import io

def twitter_page_loader(gemini_api_key, apify_api_key, op_path):
    company_name = st.text_input("Enter the company name: ")
    account = st.text_input("Enter account username: ")
    account = [account]
    since = st.date_input("Enter the 'since' date (YYYY-MM-DD): ")
    until = st.date_input("Enter the 'until' date (YYYY-MM-DD): ")
    num_tweets = st.number_input("Enter the number of tweets: ", min_value=1, value=10)
    num_queries = st.number_input("Enter the number of hashtags: ", min_value=0, value=0)
    search_queries = [st.text_input(f"Enter hashtag {i + 1}: ") for i in range(num_queries)]

    if st.button("Analyze"):
        df, filename = twitter.run(apify_api_key, gemini_api_key, company_name, 1, account, num_tweets, search_queries, since, until, num_tweets, op_path)
        st.write("Twitter details.")
        st.dataframe(df)
        filename = os.path.join(op_path, filename)

        with open(filename, "rb") as f:
            st.download_button(
                label="Download Data",
                data=f,
                file_name=filename,
                mime="application/xlsx"
            )