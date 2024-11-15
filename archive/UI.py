import streamlit as st
from PIL import Image
import base64

# Set page config
st.set_page_config(
    page_title="DigitalNova",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling
# st.markdown("""
#     <style>
#     .main-title {
#         font-size: 2.5rem;
#         font-weight: bold;
#         margin-bottom: 0.5rem;
#     }
#     .sub-title {
#         font-size: 1.5rem;
#         color: #666;
#         margin-bottom: 2rem;
#     }
#     .stTabs [data-baseweb="tab-list"] {
#         gap: 2rem;
#     }
#     .stTabs [data-baseweb="tab"] {
#         height: 50px;
#         padding: 10px 20px;
#         font-size: 1.1rem;
#     }
#     </style>
# """, unsafe_allow_html=True)

def main():
    # Sidebar
    with st.sidebar:
        # Logo placeholder
        # st.image("image.png", caption="", use_column_width=True)
        
        # Application name
        st.header("__DigitalNova__")
        
        # Navigation dropdown
        page = st.selectbox(
            "Navigation",
            ["Login", "Signup", "Home Page", "Dashboard", "Page 3"]
        )

    # Main content area
    st.header("__Digital Nova__")
    st.subheader("Data Scraping - Theme Generation - Analytics")
    
    # Content based on selected page
    if page == "Login":
        display_login_page()
    elif page == "Signup":
        display_signup_page()
    elif page == "Home Page":
        display_home_page()
    elif page == "Dashboard":
        display_dashboard_page()
    else:
        display_page_3()

def display_login_page():
    tabs = st.tabs(["Tab 1", "Tab 2", "Tab 3"])
    
    with tabs[0]:
        st.markdown("""
        ### Login Page - Tab 1
        This is sample content for Tab 1 of the Login page.
        - Point 1
        - Point 2
        - Point 3
        """)
    
    with tabs[1]:
        st.markdown("""
        ### Login Page - Tab 2
        This is sample content for Tab 2 of the Login page.
        ```python
        # Sample code block
        def hello_world():
            print("Hello from Tab 2!")
        ```
        """)
    
    with tabs[2]:
        st.markdown("""
        ### Login Page - Tab 3
        This is sample content for Tab 3 of the Login page.
        > This is a blockquote with sample text.
        """)

def display_signup_page():
    tabs = st.tabs(["Tab 1", "Tab 2", "Tab 3"])
    
    with tabs[0]:
        st.markdown("""
        ### Signup Page - Tab 1
        This is sample content for Tab 1 of the Signup page.
        - Feature 1
        - Feature 2
        - Feature 3
        """)
    
    with tabs[1]:
        st.markdown("""
        ### Signup Page - Tab 2
        This is sample content for Tab 2 of the Signup page.
        1. Step One
        2. Step Two
        3. Step Three
        """)
    
    with tabs[2]:
        st.markdown("""
        ### Signup Page - Tab 3
        This is sample content for Tab 3 of the Signup page.
        | Column 1 | Column 2 |
        |----------|----------|
        | Data 1   | Data 2   |
        """)

def display_home_page():
    tabs = st.tabs(["Tab 1", "Tab 2", "Tab 3"])
    
    with tabs[0]:
        st.markdown("""
        ### Home Page - Tab 1
        Welcome to the home page! This is Tab 1 content.
        """)
    
    with tabs[1]:
        st.markdown("""
        ### Home Page - Tab 2
        Explore our features in Tab 2.
        """)
    
    with tabs[2]:
        st.markdown("""
        ### Home Page - Tab 3
        Additional information in Tab 3.
        """)

def display_dashboard_page():
    tabs = st.tabs(["Tab 1", "Tab 2", "Tab 3"])
    
    with tabs[0]:
        st.markdown("""
        ### Dashboard - Tab 1
        Overview of key metrics and statistics.
        """)
    
    with tabs[1]:
        st.markdown("""
        ### Dashboard - Tab 2
        Detailed analytics and reports.
        """)
    
    with tabs[2]:
        st.markdown("""
        ### Dashboard - Tab 3
        Additional dashboard features.
        """)

def display_page_3():
    tabs = st.tabs(["Tab 1", "Tab 2", "Tab 3"])
    
    with tabs[0]:
        st.markdown("""
        ### Page 3 - Tab 1
        Content for Page 3, Tab 1.
        """)
    
    with tabs[1]:
        st.markdown("""
        ### Page 3 - Tab 2
        Content for Page 3, Tab 2.
        """)
    
    with tabs[2]:
        st.markdown("""
        ### Page 3 - Tab 3
        Content for Page 3, Tab 3.
        """)

if __name__ == "__main__":
    main()