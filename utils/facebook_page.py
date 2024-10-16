import streamlit as st
import os
from modules import facebook
import zipfile
import io
from datetime import datetime

# Function to calculate month difference
def month_difference(date1_str, date2_str):
    # Convert strings to datetime objects
    date_format = "%Y-%m-%d"
    date1 = datetime.strptime(date1_str, date_format)
    date2 = datetime.strptime(date2_str, date_format)
    
    # Calculate month difference
    month_diff = (date2.year - date1.year) * 12 + (date2.month - date1.month)
    
    return abs(month_diff)

def facebook_page_loader(gemini_api_key, apify_api_key, op_path):
    account_handles = []
    handle = st.text_input(f"Facebook account URL: ")
    
    max_posts = st.number_input("Max Posts Per Month", min_value=1, value=5)

    start_date = st.date_input("Start Date (Older)")
    end_date = st.date_input("End Date (Newer)")

    diff = month_difference(str(start_date), str(end_date))
    max_posts = max_posts * diff * 1.5
    max_posts = round(max_posts)
    max_posts = int(max_posts)

    if st.button("Analyze"):
        acc_df, post_df, acc_file, post_file = facebook.run(gemini_api_key, apify_api_key, handle, start_date, end_date, max_posts, op_path)
        
        df = acc_df
        df_posts = post_df
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
