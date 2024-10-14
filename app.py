import streamlit as st
import os
from modules import instagram, amazon_reviews, tripadvisor, booking, google_news, youtube, twitter, flickr
from utils import instagram_page
import zipfile
import io

# gemini_api_key = os.getenv('GEMINI_API_KEY')
# apify_api_key = os.getenv('APIFY_API_KEY')
# op_path = os.getenv('OP_PATH')

gemini_api_key = 'AIzaSyAjDT14MAn93D1xJMsBtHeaNThaFIYeLbs'
# apify_api_key = 'apify_api_eQL36WHTap9vl7eUsHIgjjcwWKqRL50NAMOS'
apify_api_key = 'apify_api_KVxCV4c7NI3aUMUCDW2Wv4GjCzTgZu4awEVM'
op_path = 'output'

if not os.path.exists(op_path):
    os.makedirs(op_path)

def main():
    st.set_page_config(page_title="Data Nova", page_icon="📊")

    st.title("Data Nova")
    st.subheader("Transforming Big Data into Strategic Insights")

    category = st.selectbox("Select Category", ["Social Media", "e-WOM", "News"])

    if category == "Social Media":
        platform = st.selectbox("Platform Selection", ["Instagram", "YouTube", "Twitter", "Flickr"])
    elif category == "e-WOM":
        platform = st.selectbox("Platform Selection", ["Amazon Product Reviews", "TripAdvisor reviews", "Booking.com reviews"])
    elif category == "News":
        platform = st.selectbox("Platform Selection", ["Google News"])


    if platform == "Instagram":        
        # account_handles = []
        # handle = st.text_input(f"Instagram account handle: ")
        # account_handles.append(handle)
        
        # time_frame = st.selectbox("Time Frame Selection (months)", [6, 12, 24])
        
        # max_posts = st.number_input("Max Posts Per Month", min_value=1, value=5)
        # filter_by_hashtags = st.radio("Filter by Hashtags", ["Yes", "No"])

        # if filter_by_hashtags == "Yes":
        #     num_hashtags = st.number_input("Number of hashtags", min_value=1, value=1)
        #     hashtags = []
        #     for i in range(num_hashtags):
        #         hashtag = st.text_input(f"Hashtag {i+1}: ")
        #         hashtags.append(hashtag)
        
        # if st.button("Analyze"):
        #     if filter_by_hashtags == "Yes":
        #         list_of_account_dataframes, list_of_posts_dataframes, acc_file, post_file = instagram.run(gemini_api_key, apify_api_key, account_handles, "b", max_posts, 1, 1, 1, time_frame, op_path, hashtags)
        #     else:
        #         list_of_account_dataframes, list_of_posts_dataframes, acc_file, post_file = instagram.run(gemini_api_key, apify_api_key, account_handles, "b", max_posts, 1, 1, 1, time_frame, op_path)
            
        #     df = list_of_account_dataframes[0]
        #     df_posts = list_of_posts_dataframes[0]
        #     st.write("Instagram account profile details.")
        #     st.dataframe(df)
        #     st.write("Instagram account posts details.")
        #     st.dataframe(df_posts)
        #     acc_file_path = os.path.join(op_path, acc_file)
        #     post_file_path = os.path.join(op_path, post_file)
        #     zip_buffer = io.BytesIO()
        #     with zipfile.ZipFile(zip_buffer, 'w') as zipf:
        #         zipf.write(acc_file_path, os.path.basename(acc_file))
        #         zipf.write(post_file_path, os.path.basename(post_file))

        #     zip_buffer.seek(0)

        #     st.download_button(
        #         label="Download ZIP",
        #         data=zip_buffer,
        #         file_name="instagram_data.zip",
        #         mime="application/zip"
        #     )
        instagram_page.instagram_page_loader(gemini_api_key, apify_api_key, op_path)
    
    elif platform == "TripAdvisor reviews":
        num_reviews = st.number_input("Number of reviews", min_value=5, value=5)
        link = st.text_input(f"Tripadvisor property URL: ")
        links = []
        links.append(link)
        if st.button("Analyze"):
            df, trip_file_name = tripadvisor.run(gemini_api_key, apify_api_key, links, num_reviews, op_path)
            st.write("Tripadvisor reviews details.")
            st.dataframe(df)
            trip_file_name = os.path.join(op_path, trip_file_name)
            with open(trip_file_name, "rb") as f:
                st.download_button(
                    label="Download Data",
                    data=f,
                    file_name=trip_file_name,
                    mime="application/xlsx"
                )

    elif platform == "Amazon Product Reviews":
        num_reviews = st.number_input("Number of reviews", min_value=5, value=5)
        link = st.text_input(f"Amazon Product URL: ")
        links = []
        links.append(link)
        
        if st.button("Analyze"):
            df, amazon_file_name = amazon_reviews.run(apify_api_key, links, op_path, num_reviews)
            st.write("Amazon product reviews details.")
            st.dataframe(df)
            amazon_file_name = os.path.join(op_path, amazon_file_name)
            with open(amazon_file_name, "rb") as f:
                st.download_button(
                    label="Download Data",
                    data=f,
                    file_name=amazon_file_name,
                    mime="application/xlsx"
                )
    elif platform == "Booking.com reviews":
        num_reviews = st.number_input("Number of reviews", min_value=5, value=5)
        link = st.text_input(f"Booking.com property URL: ")
        links = []
        links.append(link)
        
        if st.button("Analyze"):
            df, booking_file_name = booking.run(apify_api_key, links, num_reviews, op_path)
            st.write("Booking.com property reviews details.")
            st.dataframe(df)
            booking_file_name = os.path.join(op_path, booking_file_name)
            with open(booking_file_name, "rb") as f:
                st.download_button(
                    label="Download Data",
                    data=f,
                    file_name=booking_file_name,
                    mime="application/xlsx"
                )
    elif platform == "Google News":
        query = st.text_input("Enter the query: ")
        start_date = st.date_input('Enter the start date (older date)')
        end_date = st.date_input('Enter the end date (new date)')
        max_articles = st.number_input('Max news articles', min_value=2, value=5)
        if st.button("Analyze"):
            df, google_file_name = google_news.run(apify_api_key, gemini_api_key, query, max_articles, start_date, end_date, op_path)
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
    elif platform == "YouTube":
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

    elif platform == "Twitter":

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
    elif platform == "Flickr":
        query = st.text_input("Enter the query: ")
        query = [query]
        max_posts = st.number_input("Max Posts", min_value=1, value=5)
        if st.button("Analyze"):
            df, flickr_file_name = flickr.run(apify_api_key, gemini_api_key, query, max_posts, op_path)
            st.write("Flickr details.")
            st.dataframe(df)
            flickr_file_name = os.path.join(op_path, flickr_file_name)
            with open(flickr_file_name, "rb") as f:
                st.download_button(
                    label="Download Data",
                    data=f,
                    file_name=flickr_file_name,
                    mime="application/xlsx"
                )

if __name__ == "__main__":
    main()