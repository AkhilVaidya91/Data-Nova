import streamlit as st
import os
from modules import facebook
import zipfile
from gridfs import GridFS
from pymongo import MongoClient
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

def facebook_page_loader(gemini_api_key, apify_api_key, op_path, username):
    MONGO_URI = os.getenv('MONGO_URI')
    MONGO_URI = "mongodb+srv://akhilvaidya22:qN2dxc1cpwD64TeI@digital-nova.cbbsn.mongodb.net/?retryWrites=true&w=majority&appName=digital-nova"

    client = MongoClient(MONGO_URI)
    db = client['digital_nova']  # Use your existing MongoDB connection
    fs = GridFS(db)
    account_handles = []
    handle = st.text_input(f"Facebook account URL: ", key="facebook_account")
    
    max_posts = st.number_input("Max Posts Per Month", min_value=1, value=5, key="facebook_max_posts")

    start_date = st.date_input("Start Date (Older)", key="facebook_start_date")
    end_date = st.date_input("End Date (Newer)", key="facebook_end_date")

    diff = month_difference(str(start_date), str(end_date))
    max_posts = max_posts * diff * 1.5
    max_posts = round(max_posts)
    max_posts = int(max_posts)

    if st.button("Analyze", key="facebook_analyze"):
        acc_df, post_df, acc_file, post_file = facebook.run(gemini_api_key, apify_api_key, handle, start_date, end_date, max_posts, op_path, username)
        
        df = acc_df
        df_posts = post_df
        st.write("Instagram account profile details.", key="facebook_profile")
        st.dataframe(df, key="facebook_profile_df")
        st.write("Instagram account posts details.", key="facebook_posts")
        st.dataframe(df_posts, key="facebook_posts_df")

        excel_buffer = io.BytesIO()
        df.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        file_id_acc = fs.put(
            excel_buffer.getvalue(),
            filename=acc_file,
            metadata={
                'username': username,
                'file_type': 'Facebook Account Details',
                'timestamp': datetime.now()
            }
        )

        excel_buffer = io.BytesIO()
        df_posts.to_excel(excel_buffer, index=False)
        excel_buffer.seek(0)
        file_id_posts = fs.put(
            excel_buffer.getvalue(),
            filename=post_file,
            metadata={
                'username': username,
                'file_type': 'Facebook Post Details',
                'timestamp': datetime.now()
            }
        )
        # acc_file_path = os.path.join(op_path, acc_file)
        # post_file_path = os.path.join(op_path, post_file)

        grid_file = fs.get(file_id_acc)
        file_data_acc = grid_file.read()

        grid_file = fs.get(file_id_posts)
        file_data_posts = grid_file.read()

        zip_buffer = io.BytesIO()
        with zipfile.ZipFile(zip_buffer, 'w') as zipf:
            zipf.writestr(acc_file, file_data_acc)
            zipf.writestr(post_file, file_data_posts)

        zip_buffer.seek(0)

        st.download_button(
            label="Download ZIP",
            data=zip_buffer,
            file_name="instagram_data.zip",
            mime="application/zip",
            key="facebook_download"
        )
