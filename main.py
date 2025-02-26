import streamlit as st
import os
# import sqlite3
import hashlib
from pymongo import MongoClient
from modules import corpus_upload, dashboard, analytics, theme_upload
from utils import instagram_page, tripadvisor_page, website_page, facebook_page, amazon_page, booking_page, google_news_page, youtube_page, twitter_page, flickr_page, google_reviews_page

MONGO_URI = os.getenv('MONGO_URI')
MONGO_URI = "mongodb+srv://akhilvaidya22:qN2dxc1cpwD64TeI@digital-nova.cbbsn.mongodb.net/?retryWrites=true&w=majority&appName=digital-nova"

client = MongoClient(MONGO_URI)
db = client['digital_nova']
users_collection = db['users']
corpus_collection = db['corpus']
theme_collection = db['themes']

# Helper functions
def make_hashes(password):
    return hashlib.sha256(str.encode(password)).hexdigest()

def check_hashes(password, hashed_text):
    if make_hashes(password) == hashed_text:
        return hashed_text
    return False

def add_userdata(username, password, name, email, role, apify_api_key_ip, gemini_api_key_ip, openai_api_key_ip, perplexity_api_key_ip, youtube_api_key_ip):
    hashed_password = make_hashes(password)
    users_collection.insert_one({'username': username, 'password': hashed_password, 'name': name, 'email': email, 'role': role, 'api_keys': {'apify': apify_api_key_ip, 'gemini': gemini_api_key_ip, 'openai': openai_api_key_ip, 'perplexity': perplexity_api_key_ip, 'YouTube': youtube_api_key_ip}})

def login_user(username, password):
    hashed_password = make_hashes(password)
    user = users_collection.find_one({'username': username, 'password': hashed_password})
    return user

def view_all_users():
    users = users_collection.find()
    return list(users)

def welcome_screen():
    st.title("🚀 Digital Nova")
    st.subheader("Your GenAI-based research companion")
    
    st.markdown("""
    Digital Nova is your all-in-one research companion powered by advanced AI technology. Our platform helps you gather, analyze, and understand data from various sources across the internet.

    #### What we offer:

    🔍 **Multi-Platform Data Collection**
    - 📸 Social Media (Instagram, YouTube, Twitter, Flickr, Facebook)
    - 💬 Customer Reviews (Amazon, TripAdvisor, Booking.com)
    - 📰 News Articles (Google News)

    💡 **Theme Generation and Data Structuring**
    - 🤖 Generate chat-based themes using **Perplexity**.
    - 📊 Structure large document corpora into easily digestible tables using **OpenAI**.

    📈 **Corpus Analytics**
    - 🔎 Perform comparative and correlation analytics on structured themes and documents.
    - 🧩 Discover connections and insights from themes, sub-themes, and structured corpora.

    #### Get Started
    👉 Please login or create an account using the sidebar to access these powerful features and begin your research journey!

    ---
    """)

# Login/Signup sidebar
def sidebar_login_signup():
    st.sidebar.title("🚀 Digital Nova")
    menu = ["🔐 Login", "📝 SignUp"]
    choice = st.sidebar.selectbox("Menu", menu)

    if choice == "🔐 Login":
        username = st.sidebar.text_input("👤 User Name")
        password = st.sidebar.text_input("🔑 Password", type='password')
        if st.sidebar.button("🚪 Login"):
            result = login_user(username, password)
            if result:
                st.sidebar.success(f"✅ Logged In as {username}")
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.active_section = "Corpus Management"
                st.session_state.active_tab = "Data Collection"
            else:
                st.sidebar.warning("❌ Incorrect Username/Password")

    elif choice == "📝 SignUp":
        name = st.sidebar.text_input("👤 Full Name", key="name")
        email = st.sidebar.text_input("📧 Email ID", key="email")
        role = st.sidebar.selectbox("🎓 Role", ["👩‍🎓 Student", "🔬 Researcher", "👨‍🏫 Professor", "👥 Teaching Assistant"], key="role")
        new_user = st.sidebar.text_input("👤 Username" , key="new_user")
        new_password = st.sidebar.text_input("🔑 Password", type='password' , key="new_password")
        apify_api_key_ip = st.sidebar.text_input("🔑 Apify API Key", key="apify_api_key_ip")
        gemini_api_key_ip = st.sidebar.text_input("🔑 Gemini API Key", key="gemini_api_key_ip")
        openai_api_key_ip = st.sidebar.text_input("🔑 OpenAI API Key", key="openai_api_key_ip")
        perplexity_api_key_ip = st.sidebar.text_input("🔑 Perplexity API Key", key="perplexity_api_key_ip")
        youtube_api_key_ip = st.sidebar.text_input("🔑 YouTube API Key", key="youtube_api_key_ip")
        if st.sidebar.button("📩 Signup"):
            add_userdata(new_user, new_password, name, email, role, apify_api_key_ip, gemini_api_key_ip, openai_api_key_ip, perplexity_api_key_ip, youtube_api_key_ip)
            st.sidebar.success("✅ You have successfully created an account")
            st.sidebar.info("👉 Go to Login Menu to login")

def data_collection_page():
    # st.title("📊 Data Collection")
    # st.subheader("Gather data from various online sources")
    
    op_path = os.getenv('OP_PATH', 'output')
    if not os.path.exists(op_path):
        os.makedirs(op_path)
    
    user = st.session_state.username
    apify_key = users_collection.find_one({'username': user}).get('api_keys', {}).get('apify', None)
    perplexity_key = users_collection.find_one({'username': user}).get('api_keys', {}).get('perplexity', None)
    gemini_key = users_collection.find_one({'username': user}).get('api_keys', {}).get('gemini', None)
    youtube_key = users_collection.find_one({'username': user}).get('api_keys', {}).get('YouTube', None)

    apify_api_key = apify_key
    perplexity_api_key = perplexity_key
    gemini_api_key = gemini_key

    # Warning for missing API keys
    if not apify_api_key:
        st.warning("🚫 Please add your Apify API key in your user profile to proceed.")
    
    if not gemini_api_key:
        st.warning("🚫 Please add your Gemini API key in your user profile to proceed.")

    categories = ["📱 Social Media", "💬 e-WOM", "📰 News", "🌐 Website"]
    category_tabs = st.tabs(categories)
    
    for category, tab in zip(categories, category_tabs):
        with tab:
            if category == "📱 Social Media":
                platform = st.selectbox(
                    "Platform Selection", 
                    ["Instagram", "YouTube", "Twitter", "Flickr", "Facebook"],
                    key="social_media_platform"
                )
                
                if platform == "Instagram":
                    if apify_api_key and gemini_api_key:
                        instagram_page.instagram_page_loader(gemini_api_key, apify_api_key, op_path, username=st.session_state.username)
                elif platform == "YouTube":
                    if not youtube_key:
                        st.warning("Please add your YouTube API key in your user profile to proceed.")
                    else:
                        youtube_page.youtube_page_loader(op_path, st.session_state.username, youtube_key)
                elif platform == "Twitter":
                    if apify_api_key and gemini_api_key:
                        twitter_page.twitter_page_loader(gemini_api_key, apify_api_key, op_path, st.session_state.username)
                elif platform == "Flickr":
                    if apify_api_key and gemini_api_key:
                        flickr_page.flickr_page_loader(gemini_api_key, apify_api_key, op_path, st.session_state.username)
                elif platform == "Facebook":
                    if apify_api_key and gemini_api_key:
                        facebook_page.facebook_page_loader(gemini_api_key, apify_api_key, op_path, st.session_state.username)
                    
            elif category == "💬 e-WOM":
                ewom_category = st.selectbox(
                    "Select e-WOM Category", 
                    ["e-Commerce Product reviews", "Travel/Booking aggregators"],
                    key="ewom_category"
                )
                
                if ewom_category == "e-Commerce Product reviews":
                    platform = st.selectbox(
                        "Platform Selection", 
                        ["Amazon Product Reviews", "Google Reviews"],
                        key="ecommerce_platform"
                    )
                    
                    if platform == "Amazon Product Reviews":
                        if apify_api_key:
                            amazon_page.amazon_page_loader(apify_api_key, op_path, st.session_state.username)
                    elif platform == "Google Reviews":
                        if apify_api_key and gemini_api_key:
                            google_reviews_page.google_reviews_page_loader(gemini_api_key, apify_api_key, op_path, st.session_state.username)
                            
                elif ewom_category == "Travel/Booking aggregators":
                    platform = st.selectbox(
                        "Platform Selection", 
                        ["TripAdvisor reviews", "Booking.com reviews"],
                        key="travel_platform"
                    )
                    
                    if platform == "TripAdvisor reviews":
                        if apify_api_key and gemini_api_key:
                            tripadvisor_page.tripadvisor_page_loader(gemini_api_key, apify_api_key, op_path, st.session_state.username)
                    elif platform == "Booking.com reviews":
                        if apify_api_key:
                            booking_page.booking_page_loader(apify_api_key, op_path, st.session_state.username)
                            
            elif category == "📰 News":
                platform = st.selectbox(
                    "Platform Selection", 
                    ["Google News"],
                    key="news_platform"
                )
                
                if platform == "Google News":
                    if not perplexity_api_key:
                        st.warning("Please add your Perplexity API key in your user profile to proceed.")
                    elif apify_api_key and gemini_api_key:
                        google_news_page.google_news_page_loader(apify_api_key, gemini_api_key, perplexity_api_key, op_path, st.session_state.username)
                        
            elif category == "🌐 Website":
                platform = st.selectbox(
                    "Platform Selection", 
                    ["Scrape website with AI"],
                    key="website_platform"
                )
                
                if platform == "Scrape website with AI":
                    website_page.website_page_loader(st.session_state.username)

def corpus_pdf_upload_page():
    # st.title("📑 Corpus PDF Upload")
    st.info("This feature is currently being implemented. Check back soon!")

def corpus_excel_page():
    # st.title("📊 Corpus Excel Upload")
    st.info("This feature is currently being implemented. Check back soon!")

def tcm_ado_synthesis_page():
    # st.title("🔄 TCM ADO Synthesis")
    st.info("This feature is currently being implemented. Check back soon!")

def main_app():
    st.title("🚀 Digital Nova")
    st.subheader("Your GenAI-based research companion")
    
    # Model selection in sidebar (preserved from original)
    model_selections = ["OpenAI", "Gemini", "Llama", "Mistral", "DeepSeek R1"]
    embedding_model_selections = ["OpenAI", "Gemini", "USE", "MiniLM - distilBERT"]
    
    st.sidebar.header("Model Settings")
    embedding_choice = st.sidebar.selectbox("Select Embedding Model", embedding_model_selections)
    model_choice = st.sidebar.selectbox("Select LLM", model_selections)
    api_key_sidebar_input = st.sidebar.text_input("Enter API Key")

    st.session_state.model_choice = model_choice
    st.session_state.embedding_choice = embedding_choice
    st.session_state.api_key = api_key_sidebar_input

    # New navigation structure
    st.sidebar.header("Navigation")
    sections = ["Corpus Management", "Deductive Coding", "Analytics", "Dashboard"]
    active_section = st.sidebar.selectbox("Select Section", sections, index=sections.index(st.session_state.get('active_section', "Corpus Management")))
    
    # Update session state with current section
    st.session_state.active_section = active_section
    
    # Display appropriate content based on selected section
    if active_section == "Corpus Management":
        corpus_tabs = ["Data Collection", "Corpus PDF Upload", "Corpus Excel", "TCM ADO Synthesis"]
        active_tab = st.radio("Select Option", corpus_tabs, horizontal=True, index=corpus_tabs.index(st.session_state.get('active_tab', "Data Collection")))
        st.session_state.active_tab = active_tab
        
        if active_tab == "Data Collection":
            data_collection_page()
        elif active_tab == "Corpus PDF Upload":
            corpus_pdf_upload_page()
        elif active_tab == "Corpus Excel":
            corpus_excel_page()
        elif active_tab == "TCM ADO Synthesis":
            tcm_ado_synthesis_page()
            
    elif active_section == "Deductive Coding":
        theme_upload.theme_page(st.session_state.username, st.session_state.embedding_choice, st.session_state.api_key)
        
    elif active_section == "Analytics":
        analytics.analytics_page(st.session_state.username, st.session_state.model_choice, st.session_state.api_key)
        
    elif active_section == "Dashboard":
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