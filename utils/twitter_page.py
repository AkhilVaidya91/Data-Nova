import streamlit as st
import os
from modules import twitter
import zipfile
import io

def twitter_page_loader(gemini_api_key, apify_api_key, op_path, username):
    company_name = st.text_input("Enter the company name: ", key="twitter_company_name")
    account = st.text_input("Enter account username: ", key="twitter_account")
    account = [account]
    since = st.date_input("Enter the 'since' date (YYYY-MM-DD): ", key="twitter_since")
    until = st.date_input("Enter the 'until' date (YYYY-MM-DD): ", key="twitter_until")
    num_tweets = st.number_input("Enter the number of tweets: ", min_value=1, value=10, key="twitter_num_tweets")
    num_queries = st.number_input("Enter the number of hashtags: ", min_value=0, value=0, key="twitter_num_queries")
    search_queries = [st.text_input(f"Enter hashtag {i + 1}: ", key=f"twitter_hashtag_{i+1}") for i in range(num_queries)]

    if st.button("Analyze", key="twitter_analyze"):
        df, filename = twitter.run(apify_api_key, gemini_api_key, company_name, 1, account, num_tweets, search_queries, since, until, num_tweets, op_path, username)
        st.write("Twitter details.", key="twitter_details")
        st.dataframe(df, key="twitter_df")
        filename = os.path.join(op_path, filename)

        with open(filename, "rb") as f:
            st.download_button(
                label="Download Data",
                data=f,
                file_name=filename,
                mime="application/xlsx",
                key="twitter_download_button"
            )