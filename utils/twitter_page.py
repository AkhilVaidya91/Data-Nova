import streamlit as st
import os
from modules import twitter
import zipfile
from gridfs import GridFS
from pymongo import MongoClient
import io
from datetime import datetime

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
        MONGO_URI = os.getenv('MONGO_URI')
        MONGO_URI = "mongodb+srv://akhilvaidya22:qN2dxc1cpwD64TeI@digital-nova.cbbsn.mongodb.net/?retryWrites=true&w=majority&appName=digital-nova"

        client = MongoClient(MONGO_URI)
        db = client['digital_nova']  # Use your existing MongoDB connection
        fs = GridFS(db)

        df, filename = twitter.run(apify_api_key, gemini_api_key, company_name, 1, account, num_tweets, search_queries, since, until, num_tweets, op_path, username)
        st.write("Twitter details.", key="twitter_details")
        st.dataframe(df, key="twitter_df")

        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        file_id = fs.put(
            excel_buffer.getvalue(),
            filename=filename,
            metadata={
                'username': username,
                'file_type': 'Twitter Data',
                'timestamp': datetime.now()
            }
        )

        grid_file = fs.get(file_id)
        file_data = grid_file.read()

        # filename = os.path.join(op_path, filename)

        # with open(filename, "rb") as f:
        st.download_button(
            label="Download Data",
            data=file_data,
            file_name=filename,
            mime="application/xlsx",
            key="twitter_download_button"
        )