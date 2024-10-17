import streamlit as st
import os
# from modules import instagram, amazon_reviews, tripadvisor, booking, google_news, youtube, twitter, flickr
from utils import instagram_page, tripadvisor_page, website_page, facebook_page, amazon_page, booking_page, google_news_page, youtube_page, twitter_page, flickr_page
# import zipfile
# import io

gemini_api_key = os.getenv('GEMINI_API_KEY')
apify_api_key = os.getenv('APIFY_API_KEY')
op_path = os.getenv('OP_PATH')

if not os.path.exists(op_path):
    os.makedirs(op_path)

def main():
    st.set_page_config(page_title="Data Nova", page_icon="📊")

    st.title("Data Nova")
    st.subheader("Transforming Big Data into Strategic Insights")

    category = st.selectbox("Select Category", ["Social Media", "e-WOM", "News", "Website"])

    if category == "Social Media":
        platform = st.selectbox("Platform Selection", ["Instagram", "YouTube", "Twitter", "Flickr", "Facebook"])
    elif category == "e-WOM":
        category = st.selectbox("Select e-WOM Category", ["e-Commerce Product reviews", "Travel/Booking aggregators"])
        if category == "e-Commerce Product reviews":
            platform = st.selectbox("Platform Selection", ["Amazon Product Reviews", "Google Reviews"])
        elif category == "Travel/Booking aggregators":
            platform = st.selectbox("Platform Selection", ["TripAdvisor reviews", "Booking.com reviews"])
    elif category == "News":
        platform = st.selectbox("Platform Selection", ["Google News"])
    elif category == "Website":
        platform = st.selectbox("Platform Selection", ["Scrape website with AI"])


    if platform == "Instagram":        
        instagram_page.instagram_page_loader(gemini_api_key, apify_api_key, op_path)
    
    elif platform == "TripAdvisor reviews":
        tripadvisor_page.tripadvisor_page_loader(gemini_api_key, apify_api_key, op_path)

    elif platform == "Amazon Product Reviews":
        amazon_page.amazon_page_loader(apify_api_key, op_path)

    elif platform == "Booking.com reviews":
        booking_page.booking_page_loader(apify_api_key, op_path)

    elif platform == "Google News":
        google_news_page.google_news_page_loader(apify_api_key, gemini_api_key, op_path)

    elif platform == "YouTube":
        youtube_page.youtube_page_loader(op_path)

    elif platform == "Twitter":
        twitter_page.twitter_page_loader(gemini_api_key, apify_api_key, op_path)

    elif platform == "Flickr":
        flickr_page.flickr_page_loader(gemini_api_key, apify_api_key, op_path)

    elif platform == "Scrape website with AI":
        website_page.website_page_loader()

    elif platform == "Facebook":
        facebook_page.facebook_page_loader(gemini_api_key, apify_api_key, op_path)

if __name__ == "__main__":
    main()