import streamlit as st
import os
import sqlite3
import hashlib
from utils import instagram_page, tripadvisor_page, website_page, facebook_page, amazon_page, booking_page, google_news_page, youtube_page, twitter_page, flickr_page

# SQLite setup
conn = sqlite3.connect('users.db', check_same_thread=False)
c = conn.cursor()

# Create users table
c.execute('''CREATE TABLE IF NOT EXISTS users
             (username TEXT PRIMARY KEY, password TEXT)''')
conn.commit()

# Helper functions
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

def add_userdata(username, password):
    c.execute('INSERT INTO users(username,password) VALUES (?,?)', (username, make_hashes(password)))
    conn.commit()

def login_user(username, password):
    c.execute('SELECT * FROM users WHERE username =? AND password = ?', (username, make_hashes(password)))
    data = c.fetchall()
    return data

def view_all_users():
    c.execute('SELECT * FROM users')
    data = c.fetchall()
    return data

# Login/Signup sidebar
def sidebar_login_signup():
    st.sidebar.title("Login/Signup")
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
    st.title("Data Nova")
    st.subheader("Transforming Big Data into Strategic Insights")

    gemini_api_key = os.getenv('GEMINI_API_KEY')
    apify_api_key = os.getenv('APIFY_API_KEY')
    op_path = os.getenv('OP_PATH')

    if not os.path.exists(op_path):
        os.makedirs(op_path)

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
    # ... (rest of the platform conditions)
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

def main():
    st.set_page_config(page_title="Data Nova", page_icon="📊")
    
    if 'logged_in' not in st.session_state:
        st.session_state.logged_in = False

    sidebar_login_signup()

    if st.session_state.logged_in:
        main_app()
    else:
        st.warning("Please log in to access the application.")

if __name__ == "__main__":
    main()