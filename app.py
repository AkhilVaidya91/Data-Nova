import streamlit as st
import os
# import sqlite3
import hashlib
from pymongo import MongoClient
from modules import themes, dashboard, analytics
from utils import instagram_page, tripadvisor_page, website_page, facebook_page, amazon_page, booking_page, google_news_page, youtube_page, twitter_page, flickr_page

MONGO_URI = os.getenv('MONGO_URI')
MONGO_URI = "mongodb+srv://akhilvaidya22:qN2dxc1cpwD64TeI@digital-nova.cbbsn.mongodb.net/?retryWrites=true&w=majority&appName=digital-nova"

client = MongoClient(MONGO_URI)
db = client['digital_nova']
users_collection = db['users']

# Helper functions
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

def add_userdata(username, password):
    hashed_password = make_hashes(password)
    users_collection.insert_one({'username': username, 'password': hashed_password})

def login_user(username, password):
    hashed_password = make_hashes(password)
    user = users_collection.find_one({'username': username, 'password': hashed_password})
    return user

def view_all_users():
    users = users_collection.find()
    return list(users)

def welcome_screen():
    st.title("Digital Nova")
    st.subheader("Your GenAI-based research companion")
    
    st.markdown("""
    ### Welcome to Digital Nova! 👋
    
    Digital Nova is your all-in-one research companion powered by advanced AI technology. Our platform helps you gather, analyze, and understand data from various sources across the internet.
    
    #### What we offer:
    
    🔍 **Multi-Platform Data Collection**
    - Social Media (Instagram, YouTube, Twitter, Flickr, Facebook)
    - Customer Reviews (Amazon, TripAdvisor, Booking.com)
    - News Articles (Google News)
    - Custom Website Scraping

    #### Get Started
    Please login or create an account using the sidebar to access these powerful features and begin your research journey!
    
    ---
    """)

# Login/Signup sidebar
def sidebar_login_signup():
    st.sidebar.title("Digital Nova")
    menu = ["Login", "SignUp"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "Login":
        username = st.sidebar.text_input("User Name")
        password = st.sidebar.text_input("Password", type='password')
        if st.sidebar.button("Login"):
            result = login_user(username, password)
            if result:
                st.sidebar.success(f"Logged In as {username}")
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.active_tab = "Data Scraping"
            else:
                st.sidebar.warning("Incorrect Username/Password")

    elif choice == "SignUp":
        new_user = st.sidebar.text_input("Username")
        new_password = st.sidebar.text_input("Password", type='password')
        if st.sidebar.button("Signup"):
            add_userdata(new_user, new_password)
            st.sidebar.success("You have successfully created an account")
            st.sidebar.info("Go to Login Menu to login")

def main_app():
    st.title("Digital Nova")
    st.subheader("Your GenAI-based research companion")
    op_path = os.getenv('OP_PATH', 'output')

    user = st.session_state.username

    apify_key = users_collection.find_one({'username': user}).get('api_keys', {}).get('apify', None)
    perplexity_key = users_collection.find_one({'username': user}).get('api_keys', {}).get('perplexity', None)
    gemini_key = users_collection.find_one({'username': user}).get('api_keys', {}).get('gemini', None)
    youtube_key = users_collection.find_one({'username': user}).get('api_keys', {}).get('YouTube', None)

    apify_api_key = apify_key
    perplexity_api_key = perplexity_key
    gemini_api_key = gemini_key

    if not os.path.exists(op_path):
        os.makedirs(op_path)
    tabs = ["Data Scraping", "Theme Generation", "Analytics", "Dashboard"]
    active_tab = st.sidebar.selectbox("Select Tab", tabs, index=tabs.index(st.session_state.get('active_tab', "Data Scraping")))
    if active_tab == "Data Scraping":
        st.session_state.active_tab = "Data Scraping"

        ## check if user has Aipfy API key
        if not apify_api_key:
            st.warning("Please add your Apify API key in the sidebar to proceed.")
            return
        
        if not gemini_api_key:
            st.warning("Please add your Gemini API key in the sidebar to proceed.")
            return

        categories = ["Social Media", "e-WOM", "News", "Website"]
        category_tabs = st.tabs(categories)
        # category = st.selectbox("Select Category", ["Social Media", "e-WOM", "News", "Website"])
        for category, tab in zip(categories, category_tabs):
            with tab:
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
                    instagram_page.instagram_page_loader(gemini_api_key, apify_api_key, op_path, username=st.session_state.username)
                elif platform == "TripAdvisor reviews":
                    tripadvisor_page.tripadvisor_page_loader(gemini_api_key, apify_api_key, op_path, st.session_state.username)

                elif platform == "Amazon Product Reviews":
                    amazon_page.amazon_page_loader(apify_api_key, op_path, st.session_state.username)

                elif platform == "Booking.com reviews":
                    booking_page.booking_page_loader(apify_api_key, op_path, st.session_state.username)

                elif platform == "Google News":
                    ## check if user has Perplexity API key
                    if not perplexity_api_key:
                        st.warning("Please add your Perplexity API key in the user profile to proceed.")
                        return
                    google_news_page.google_news_page_loader(apify_api_key, gemini_api_key, perplexity_api_key, op_path, st.session_state.username)

                elif platform == "YouTube":
                    ## checking if user has YouTube API key

                    if not youtube_key:
                        st.warning("Please add your YouTube API key in the user profile to proceed.")
                        return
                    youtube_page.youtube_page_loader(op_path, st.session_state.username, youtube_key)

                elif platform == "Twitter":
                    twitter_page.twitter_page_loader(gemini_api_key, apify_api_key, op_path, st.session_state.username)

                elif platform == "Flickr":
                    flickr_page.flickr_page_loader(gemini_api_key, apify_api_key, op_path, st.session_state.username)

                elif platform == "Scrape website with AI":
                    website_page.website_page_loader(gemini_api_key)

                elif platform == "Facebook":
                    facebook_page.facebook_page_loader(gemini_api_key, apify_api_key, op_path, st.session_state.username)
    
    elif active_tab == "Theme Generation":
        st.session_state.active_tab = "Theme Generation"
        themes.themes_main(st.session_state.username)

    elif active_tab == "Analytics":
        st.session_state.active_tab = "Analytics"
        analytics.analytics_page(st.session_state.username)

    elif active_tab == "Dashboard":
        st.session_state.active_tab = "Dashboard"
        dashboard.dashboard()


def main():
    st.set_page_config(page_title="Digital Nova", page_icon="📊", layout="wide")
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    sidebar_login_signup()

    if st.session_state.logged_in:
        main_app()
    else:
        welcome_screen()

if __name__ == "__main__":
    main()