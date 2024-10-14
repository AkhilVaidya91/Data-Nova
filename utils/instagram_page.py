import streamlit as st
import os
from modules import instagram
import zipfile
import io

def instagram_page_loader(gemini_api_key, apify_api_key, op_path):
    account_handles = []
    handle = st.text_input(f"Instagram account handle: ")
    account_handles.append(handle)
    
    time_frame = st.selectbox("Time Frame Selection (months)", [6, 12, 24])
    
    max_posts = st.number_input("Max Posts Per Month", min_value=1, value=5)
    filter_by_hashtags = st.radio("Filter by Hashtags", ["No", "Yes"])

    if filter_by_hashtags == "Yes":
        num_hashtags = st.number_input("Number of hashtags", min_value=1, value=1)
        hashtags = []
        for i in range(num_hashtags):
            hashtag = st.text_input(f"Hashtag {i+1}: ")
            hashtags.append(hashtag)
    
    if st.button("Analyze"):
        if filter_by_hashtags == "Yes":
            list_of_account_dataframes, list_of_posts_dataframes, acc_file, post_file = instagram.run(gemini_api_key, apify_api_key, account_handles, "b", max_posts, 1, 1, 1, time_frame, op_path, hashtags)
        else:
            list_of_account_dataframes, list_of_posts_dataframes, acc_file, post_file = instagram.run(gemini_api_key, apify_api_key, account_handles, "b", max_posts, 1, 1, 1, time_frame, op_path)
        
        df = list_of_account_dataframes[0]
        df_posts = list_of_posts_dataframes[0]
        st.write("Instagram account profile details.")
        st.dataframe(df)
        st.write("Instagram account posts details.")
        st.dataframe(df_posts)
        acc_file_path = os.path.join(op_path, acc_file)
        post_file_path = os.path.join(op_path, post_file)
        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zipf:
            zipf.write(acc_file_path, os.path.basename(acc_file))
            zipf.write(post_file_path, os.path.basename(post_file))

        zip_buffer.seek(0)

        st.download_button(
            label="Download ZIP",
            data=zip_buffer,
            file_name="instagram_data.zip",
            mime="application/zip"
        )
