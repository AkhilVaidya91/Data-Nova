import streamlit as st
import os
from modules import youtube
import zipfile
import io

def youtube_page_loader(op_path):
        channel_name = st.text_input("Enter the channel name: ")
        max_videos = st.number_input("Max Videos", min_value=1, value=5)

        if st.button("Analyze"):
            channel_id = youtube.get_channel_id(channel_name)
            if channel_id:
                df_channel_stats, stats_filename = youtube.save_channel_statistics_to_excel(channel_id, op_path)
                df_video_stats, videos_filename = youtube.scrape_channel_videos_to_excel(channel_id, channel_name,max_videos,3, op_path)
                st.write("Channel Statistics")
                st.dataframe(df_channel_stats)
                st.write("Channel Videos")
                st.dataframe(df_video_stats)

                stats_filename = os.path.join(op_path, stats_filename)
                videos_filename = os.path.join(op_path, videos_filename)

                zip_buffer = io.BytesIO()
                with zipfile.ZipFile(zip_buffer, 'w') as zipf:
                    zipf.write(stats_filename, os.path.basename(stats_filename))
                    zipf.write(videos_filename, os.path.basename(videos_filename))

                zip_buffer.seek(0)

                st.download_button(
                    label="Download ZIP",
                    data=zip_buffer,
                    file_name="youtube_data.zip",
                    mime="application/zip"
                )
            else:
                st.write(f"Channel Name: {channel_name}, Channel ID not found.")