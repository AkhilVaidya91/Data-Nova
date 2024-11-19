import streamlit as st
import os
from modules import youtube
import zipfile
from gridfs import GridFS
from pymongo import MongoClient
import io
from datetime import datetime

def youtube_page_loader(op_path, username, youtube_key):
        st.info(
            """
            **YouTube Channel Scraper**  
            This tool allows you to scrape and analyze data from a YouTube channel. You can extract various details including video information, transcripts, comments, and channel statistics. 

            **Features:**
            - Extract video details such as title, views, likes, comments, duration, and more.
            - Fetch transcripts (if available) for videos in English or other languages.

            **Prerequisites:**
            - A valid YouTube API key to access YouTube data.
            - Ensure you have enabled the YouTube API in your Google Cloud Console.
            """
        )

        channel_name = st.text_input("Enter the channel name: ", key="youtube_channel_name")
        max_videos = st.number_input("Max Videos", min_value=1, value=5, key="youtube_max_videos")

        if st.button("Analyze", key="youtube_analyze"):
            MONGO_URI = os.getenv('MONGO_URI')
            MONGO_URI = "mongodb+srv://akhilvaidya22:qN2dxc1cpwD64TeI@digital-nova.cbbsn.mongodb.net/?retryWrites=true&w=majority&appName=digital-nova"

            client = MongoClient(MONGO_URI)
            db = client['digital_nova']  # Use your existing MongoDB connection
            fs = GridFS(db)

            channel_id = youtube.get_channel_id(channel_name, youtube_key)
            if channel_id:
                df_channel_stats, stats_filename = youtube.save_channel_statistics_to_excel(channel_id, op_path, username, youtube_key)
                df_video_stats, videos_filename = youtube.scrape_channel_videos_to_excel(channel_id, channel_name,max_videos,3, op_path, username, youtube_key)
                st.write("Channel Statistics", key="youtube_channel_stats")
                st.dataframe(df_channel_stats, key="youtube_channel_stats_df")
                st.write("Channel Videos", key="youtube_channel_videos")
                st.dataframe(df_video_stats, key="youtube_channel_videos_df")

                excel_buffer = io.BytesIO()
                df_channel_stats.to_excel(excel_buffer, index=False)
                excel_buffer.seek(0)
                file_id_channel = fs.put(
                    excel_buffer.getvalue(),
                    filename=stats_filename,
                    metadata={
                        'username': username,
                        'file_type': 'YouTube Channel Statistics',
                        'timestamp': datetime.now()
                    }
                )

                excel_buffer = io.BytesIO()
                df_video_stats.to_excel(excel_buffer, index=False)
                excel_buffer.seek(0)
                file_id_video = fs.put(
                    excel_buffer.getvalue(),
                    filename=videos_filename,
                    metadata={
                        'username': username,
                        'file_type': 'YouTube Video Statistics',
                        'timestamp': datetime.now()
                    }
                )

                # booking_file_name = os.path.join(op_path, booking_file_name)

                grid_file = fs.get(file_id_channel)
                file_data_channel = grid_file.read()

                grid_file = fs.get(file_id_video)
                file_data_video = grid_file.read()

                # stats_filename = os.path.join(op_path, stats_filename)
                # videos_filename = os.path.join(op_path, videos_filename)

                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w') as zipf:
                    # zipf.write(stats_filename, os.path.basename(stats_filename))
                    # zipf.write(videos_filename, os.path.basename(videos_filename))
                    zipf.writestr(stats_filename, file_data_channel)
                    zipf.writestr(videos_filename, file_data_video)

                zip_buffer.seek(0)

                st.download_button(
                    label="Download ZIP",
                    data=zip_buffer,
                    file_name="youtube_data.zip",
                    mime="application/zip",
                    key="youtube_download"
                )
            else:
                st.write(f"Channel Name: {channel_name}, Channel ID not found.", key="youtube_channel_stats")