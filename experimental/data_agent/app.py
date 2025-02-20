# import streamlit as st
# from models import LLMModelInterface
# from datetime import datetime
# import json
# from pydantic import BaseModel

# # Initialize session state variables
# if 'response_json' not in st.session_state:
#     st.session_state.response_json = None
# if 'show_instagram_search' not in st.session_state:
#     st.session_state.show_instagram_search = False
# if 'instagram_username' not in st.session_state:
#     st.session_state.instagram_username = None

# TODAY_DATE = datetime.now().strftime("%d/%m/%Y")

# # Set page configuration
# st.set_page_config(
#     page_title="AI Data Agent",
#     page_icon="🤖",
#     layout="centered",
# )

# # Title and subtitle
# st.title("AI Data Agent")
# st.subheader("Your Intelligent Assistant for Social Media Data Sourcing.")
# st.info("The prompt should include the platform name (Instagram and Facebook only for the beta version), name of the company to search for and the start and end date or duration of the search.")

# # API Keys in sidebar to keep main interface clean
# with st.sidebar:
#     st.header("API Configuration")
#     API_KEY = st.text_input("Gemini API Key", placeholder="Enter your Gemini API key...", type="password")
#     PPLX_API_KEY = st.text_input("PPLX API Key", placeholder="Enter your PPLX API key...", type="password")

# # Text input for user prompt
# user_prompt = st.text_input(
#     "Enter your query",
#     placeholder="Ask me anything about your data..."
# )

# def process_initial_search():
#     prompt_template = f"""
# You are an advanced AI system designed to extract structured information from user queries. **You are NOT required to fetch, scrape, or access real-time data from social media.** Your only task is to extract relevant keywords from the given input and return a properly formatted JSON object.

# ## Task:
# The user will provide:
# 1. A **social media platform name** (e.g., Instagram, Facebook etc.).
# 2. A **company or institute name** (mostly Indian companies or educational institutes).
# 3. A **start and end date**, which may be:
#    - Exact dates (any format).
#    - A relative time range (e.g., "6 months ago from today").
#    - A mix of both (e.g., "from Jan 2023 to now").

# ## Rules:
# 1. **Extract and standardize** the platform, company, and dates.
# 2. **Convert relative time expressions** into `DD/MM/YYYY` format using today’s date: `{TODAY_DATE}`.
# 3. **Do NOT fetch any real-time data.** Your role is only to process the given text.
# 4. **Always return a strict JSON object** with the following fields:
#    - `"platform"`: The social media platform as a string. This is an enum field with the only possible values: `"Instagram"`, `"Facebook"`, `"Other"`. If the platform is not Instagram or Facebook, set it to `"Other"`.
#    - `"company"`: The extracted company/institute name as a string.
#    - `"start_date"`: The extracted or computed start date in `DD/MM/YYYY` format.
#    - `"end_date"`: The extracted or computed end date in `DD/MM/YYYY` format.

# ## Example Inputs and Expected Outputs:

# **Example 1:**  
# User Input: *"Find Instagram posts about TCS from January 2023 to July 2023."*  
# Expected Output:
# ```json
# {{
#   "platform": "Instagram",
#   "company": "TCS",
#   "start_date": "01/01/2023",
#   "end_date": "01/07/2023"
# }}


# **STRICT RULES:** 
# - You are NOT sourcing or retrieving real-time data.
# - Do NOT generate any explanations or disclaimers.
# - ONLY output the extracted JSON object. 
# - **Do NOT** generate explanations or additional text.  
# - **ONLY** output a JSON object in the specified format. The output string should be directly parsable and shuld not contain any preceeding or trailing text. It should contain all the specified fields even if the values are empty.
# - **Ensure dates are properly formatted as `DD/MM/YYYY`.**  
# - The start date is the previous date and the end date is the more recent one.
# - If any information is missing or unclear, infer it logically but **never hallucinate** or invent non-existent details. The only two platforms are Instagram and Facebook. If the platform is not one of these, set it to "Other".
# - The user might type statements like "give me data for this platform...", you dont have to follow the explicit instruction of the user, just extract the required keywords from the query and nothing else. It's the user's goal to collect the data, you would only identify the platform, the company and the start and end date.  

# Now, process the following user query and return the structured JSON output:
# {user_prompt}"""

#     if API_KEY:
#         model = LLMModelInterface()
#         response = model.call_gemini(prompt_template, API_KEY)
#         st.session_state.response_json = json.loads(response.strip())
#         st.session_state.show_instagram_search = (
#             st.session_state.response_json.get("platform") == "Instagram"
#         )
#     else:
#         st.error("Please enter your Gemini API key!")

# def process_instagram_search():
#     if not PPLX_API_KEY:
#         st.error("Please enter your PPLX API key!")
#         return

#     platform = st.session_state.response_json.get("platform")
#     company = st.session_state.response_json.get("company")
    
#     class AnswerFormat(BaseModel):
#         username: str
    
#     pplx_prompt = f"""You are an AI agent that has access to the web. I will provide you the name of a company or an educational institute. You have to find the exact {platform} username of that company/institute. Company/Institute name is: {company}. The username should be the exact string match for the {platform} username so that I can directly search for it. Do your search only in the domain of {platform} and not the whole web to ensure that you find the exact username keyword. Give me only the username in the specified JSON format. The only key in the json is "username"."""
    
#     try:
#         json_response = LLMModelInterface.get_pplx_response(
#             AnswerFormat, 
#             pplx_prompt, 
#             PPLX_API_KEY, 
#             "https://www.instagram.com/"
#         )
#         base_json = json.loads(json_response)
#         st.session_state.instagram_username = base_json.get("username")
#         return base_json
#     except Exception as e:
#         st.error(f"Error parsing PPLX response: {e}")
#         return None

# # Initial search button
# if st.button("Search"):
#     if user_prompt:
#         process_initial_search()
#     else:
#         st.warning("Please enter a query first!")

# # Display results and Instagram search option if available
# if st.session_state.response_json:
#     st.json(st.session_state.response_json)
    
#     platform = st.session_state.response_json.get("platform")
#     company = st.session_state.response_json.get("company")
#     start_date = st.session_state.response_json.get("start_date")
#     end_date = st.session_state.response_json.get("end_date")

#     if platform == "Instagram":
#         st.info(f"Searching Instagram for posts about {company} from {start_date} to {end_date}...")
        
#         if st.button("Search Instagram"):
#             instagram_response = process_instagram_search()
#             if instagram_response:
#                 st.json(instagram_response)

#     elif platform == "Facebook":
#         st.info(f"Searching Facebook for posts about {company} from {start_date} to {end_date}...")
#     else:
#         st.error(f"Incompatible platform: {platform}. Please choose Instagram or Facebook.")




























# import streamlit as st
# from models import LLMModelInterface
# from datetime import datetime
# import json
# from smolagents import CodeAgent, HfApiModel, DuckDuckGoSearchTool

# # Initialize session state variables
# if 'response_json' not in st.session_state:
#     st.session_state.response_json = None
# if 'show_instagram_search' not in st.session_state:
#     st.session_state.show_instagram_search = False
# if 'instagram_username' not in st.session_state:
#     st.session_state.instagram_username = None

# TODAY_DATE = datetime.now().strftime("%d/%m/%Y")

# # Set page configuration
# st.set_page_config(
#     page_title="AI Data Agent",
#     page_icon="🤖",
#     layout="centered",
# )

# # Title and subtitle
# st.title("AI Data Agent")
# st.subheader("Your Intelligent Assistant for Social Media Data Sourcing.")
# st.info("The prompt should include the platform name (Instagram and Facebook only for the beta version), name of the company to search for and the start and end date or duration of the search.")

# # API Keys in sidebar to keep main interface clean
# with st.sidebar:
#     st.header("API Configuration")
#     API_KEY = st.text_input("Gemini API Key", placeholder="Enter your Gemini API key...", type="password")
#     HF_API_KEY = st.text_input("HuggingFace API Key", placeholder="Enter your HuggingFace API key...", type="password")

# # Text input for user prompt
# user_prompt = st.text_input(
#     "Enter your query",
#     placeholder="Ask me anything about your data..."
# )

# def create_web_agent(hf_token):
#     """Creates a web agent for Instagram ID search"""
#     model = HfApiModel(token=hf_token)
#     agent = CodeAgent(
#         tools=[DuckDuckGoSearchTool()],
#         model=model,
#         name="instagram_search_agent",
#         description="A specialized agent that searches for Instagram IDs"
#     )
#     return agent

# def process_initial_search():
#     prompt_template = f"""
# You are an advanced AI system designed to extract structured information from user queries. **You are NOT required to fetch, scrape, or access real-time data from social media.** Your only task is to extract relevant keywords from the given input and return a properly formatted JSON object.

# ## Task:
# The user will provide:
# 1. A **social media platform name** (e.g., Instagram, Facebook etc.).
# 2. A **company or institute name** (mostly Indian companies or educational institutes).
# 3. A **start and end date**, which may be:
#    - Exact dates (any format).
#    - A relative time range (e.g., "6 months ago from today").
#    - A mix of both (e.g., "from Jan 2023 to now").

# ## Rules:
# 1. **Extract and standardize** the platform, company, and dates.
# 2. **Convert relative time expressions** into `YYYY-MM-DD` format using today's date: `{TODAY_DATE}`.
# 3. **Do NOT fetch any real-time data.** Your role is only to process the given text.
# 4. **Always return a strict JSON object** with the following fields:
#    - `"platform"`: The social media platform as a string. This is an enum field with the only possible values: `"Instagram"`, `"Facebook"`, `"Other"`.
#    - `"company"`: The extracted company/institute name as a string.
#    - `"start_date"`: The extracted or computed start date in `YYYY-MM-DD` format.
#    - `"end_date"`: The extracted or computed end date in `YYYY-MM-DD` format.

# {user_prompt}"""

#     if API_KEY:
#         model = LLMModelInterface()
#         response = model.call_gemini(prompt_template, API_KEY)
#         st.session_state.response_json = json.loads(response.strip())
#         st.session_state.show_instagram_search = (
#             st.session_state.response_json.get("platform") == "Instagram"
#         )
#     else:
#         st.error("Please enter your Gemini API key!")

# def search_instagram_id(company_name):
#     """Search for Instagram ID using web search agent"""
#     if not HF_API_KEY:
#         st.error("Please enter your HuggingFace API key!")
#         return None
    
#     agent = create_web_agent(HF_API_KEY)
#     search_prompt = f"Find the official Instagram username/handle for {company_name}. Return ONLY the username without the @ symbol or any other text."
    
#     try:
#         instagram_id = agent.run(search_prompt).strip()
#         return {"username": instagram_id}
#     except Exception as e:
#         st.error(f"Error searching Instagram ID: {e}")
#         return None

# # Initial search button
# if st.button("Search"):
#     if user_prompt:
#         process_initial_search()
#     else:
#         st.warning("Please enter a query first!")

# # Display results and Instagram search option if available
# if st.session_state.response_json:
#     st.json(st.session_state.response_json)
    
#     platform = st.session_state.response_json.get("platform")
#     company = st.session_state.response_json.get("company")
#     start_date = st.session_state.response_json.get("start_date")
#     end_date = st.session_state.response_json.get("end_date")

#     if platform == "Instagram":
#         st.info(f"Searching Instagram for posts about {company} from {start_date} to {end_date}...")
        
#         if st.button("Find Instagram ID"):
#             instagram_response = search_instagram_id(company)
#             if instagram_response:
#                 st.json(instagram_response)

#     elif platform == "Facebook":
#         st.info(f"Searching Facebook for posts about {company} from {start_date} to {end_date}...")
#     else:
#         st.error(f"Incompatible platform: {platform}. Please choose Instagram or Facebook.")


# from apify_client import ApifyClient
# client = ApifyClient("<YOUR_API_TOKEN>")

# # Prepare the Actor input
# instagram_id = "natgeo"
# start_date = "2023-01-01"
# run_input = {
#     "username": [instagram_id],
#     # "resultsLimit": 30,
#     "onlyPostsNewerThan": start_date
# }

# # Run the Actor and wait for it to finish
# run = client.actor("apify/instagram-post-scraper").call(run_input=run_input)

# # Fetch and print Actor results from the run's dataset (if there are any)
# print("💾 Check your data here: https://console.apify.com/storage/datasets/" + run["defaultDatasetId"])
# for item in client.dataset(run["defaultDatasetId"]).iterate_items():
#     print(item)

















import streamlit as st
from models import LLMModelInterface
from datetime import datetime
import json
from smolagents import CodeAgent, HfApiModel, DuckDuckGoSearchTool
from apify_client import ApifyClient

# Initialize session state variables
if 'response_json' not in st.session_state:
    st.session_state.response_json = None
if 'show_instagram_search' not in st.session_state:
    st.session_state.show_instagram_search = False
if 'instagram_username' not in st.session_state:
    st.session_state.instagram_username = None
if 'instagram_data' not in st.session_state:
    st.session_state.instagram_data = None
if 'instagram_search_clicked' not in st.session_state:
    st.session_state.instagram_search_clicked = False
if 'fetch_data_clicked' not in st.session_state:
    st.session_state.fetch_data_clicked = False

TODAY_DATE = datetime.now().strftime("%Y-%m-%d")

# Set page configuration
st.set_page_config(
    page_title="AI Data Agent",
    page_icon="🤖",
    layout="centered",
)

# Title and subtitle
st.title("AI Data Agent")
st.subheader("Your Intelligent Assistant for Social Media Data Sourcing.")
st.info("The prompt should include the platform name (Instagram and Facebook only for the beta version), name of the company to search for and the start and end date or duration of the search.")

# API Keys in sidebar to keep main interface clean
with st.sidebar:
    st.header("API Configuration")
    API_KEY = st.text_input("Gemini API Key", placeholder="Enter your Gemini API key...", type="password")
    HF_API_KEY = st.text_input("HuggingFace API Key", placeholder="Enter your HuggingFace API key...", type="password")
    APIFY_API_KEY = st.text_input("Apify API Key", placeholder="Enter your Apify API key...", type="password")

# Text input for user prompt
user_prompt = st.text_input(
    "Enter your query",
    placeholder="Ask me anything about your data..."
)

def create_web_agent(hf_token):
    """Creates a web agent for Instagram ID search"""
    model = HfApiModel(token=hf_token)
    agent = CodeAgent(
        tools=[DuckDuckGoSearchTool()],
        model=model,
        name="instagram_search_agent",
        description="A specialized agent that searches for Instagram IDs"
    )
    return agent

def process_initial_search():
    prompt_template = f"""
You are an advanced AI system designed to extract structured information from user queries. **You are NOT required to fetch, scrape, or access real-time data from social media.** Your only task is to extract relevant keywords from the given input and return a properly formatted JSON object.

## Task:
The user will provide:
1. A **social media platform name** (e.g., Instagram, Facebook etc.).
2. A **company or institute name** (mostly Indian companies or educational institutes).
3. A **start and end date**, which may be:
   - Exact dates (any format).
   - A relative time range (e.g., "6 months ago from today").
   - A mix of both (e.g., "from Jan 2023 to now").

## Rules:
1. **Extract and standardize** the platform, company, and dates.
2. **Convert relative time expressions** into `YYYY-MM-DD` format using today's date: `{TODAY_DATE}`.
3. **Do NOT fetch any real-time data.** Your role is only to process the given text.
4. **Always return a strict JSON object** with the following fields:
   - `"platform"`: The social media platform as a string. This is an enum field with the only possible values: `"Instagram"`, `"Facebook"`, `"Other"`.
   - `"company"`: The extracted company/institute name as a string.
   - `"start_date"`: The extracted or computed start date in `YYYY-MM-DD` format.
   - `"end_date"`: The extracted or computed end date in `YYYY-MM-DD` format.

{user_prompt}"""

    if API_KEY:
        model = LLMModelInterface()
        response = model.call_gemini(prompt_template, API_KEY)
        st.session_state.response_json = json.loads(response.strip())
        st.session_state.show_instagram_search = (
            st.session_state.response_json.get("platform") == "Instagram"
        )
    else:
        st.error("Please enter your Gemini API key!")

def search_instagram_id(company_name):
    """Search for Instagram ID using web search agent"""
    if not HF_API_KEY:
        st.error("Please enter your HuggingFace API key!")
        return None
    
    agent = create_web_agent(HF_API_KEY)
    search_prompt = f"Find the official Instagram username/handle for {company_name}. Return ONLY the username without the @ symbol or any other text."
    
    try:
        instagram_id = agent.run(search_prompt).strip()
        return {"username": instagram_id}
    except Exception as e:
        st.error(f"Error searching Instagram ID: {e}")
        return None

def fetch_instagram_data(username, start_date):
    """Fetch Instagram data using Apify"""
    if not APIFY_API_KEY:
        st.error("Please enter your Apify API key!")
        return None

    try:
        client = ApifyClient(APIFY_API_KEY)
        
        # Prepare the Actor input
        run_input = {
            "username": [username],
            "onlyPostsNewerThan": f"{start_date}T00:00:00Z"
        }

        # Create a progress bar
        progress_text = "Fetching Instagram data..."
        progress_bar = st.progress(0, text=progress_text)
        
        # Run the Actor and wait for it to finish
        run = client.actor("apify/instagram-post-scraper").call(run_input=run_input)
        
        # Update progress
        progress_bar.progress(50, text="Processing data...")

        # Fetch Actor results
        data = list(client.dataset(run["defaultDatasetId"]).iterate_items())
        
        # Complete progress
        progress_bar.progress(100, text="Data fetching complete!")
        progress_bar.empty()

        return data

    except Exception as e:
        st.error(f"Error fetching Instagram data: {e}")
        return None

# Initial search button
if st.button("Search"):
    if user_prompt:
        process_initial_search()
    else:
        st.warning("Please enter a query first!")

# Display results and Instagram search option if available
if st.session_state.response_json:
    st.json(st.session_state.response_json)
    
    platform = st.session_state.response_json.get("platform")
    company = st.session_state.response_json.get("company")
    start_date = st.session_state.response_json.get("start_date")
    end_date = st.session_state.response_json.get("end_date")

    # if platform == "Instagram":
    #     st.info(f"Searching Instagram for posts about {company} from {start_date} to {end_date}...")
        
    #     # First get the Instagram ID
    #     if st.button("Find Instagram ID"):
    #         instagram_response = search_instagram_id(company)
    #         if instagram_response:
    #             st.session_state.instagram_username = instagram_response.get("username")
    #             st.json(instagram_response)
                
    #             # Show button to fetch Instagram data only after we have the username
    #             if st.session_state.instagram_username:
    #                 if st.button("Fetch Instagram Data"):
    #                     with st.spinner("Fetching Instagram data..."):
    #                         instagram_data = fetch_instagram_data(
    #                             st.session_state.instagram_username,
    #                             start_date
    #                         )
    #                         if instagram_data:
    #                             st.session_state.instagram_data = instagram_data
    #                             st.json(instagram_data)
    if platform == "Instagram":
        st.info(f"Searching Instagram for posts about {company} from {start_date} to {end_date}...")
        
        # Button to find Instagram ID
        if not st.session_state.instagram_search_clicked:
            if st.button("Find Instagram ID"):
                st.session_state.instagram_search_clicked = True
                instagram_response = search_instagram_id(company)
                if instagram_response:
                    st.session_state.instagram_username = instagram_response.get("username")
                    st.session_state.instagram_response = instagram_response

        # Display Instagram ID results if we have them
        if st.session_state.instagram_username:
            st.json(st.session_state.instagram_response)
            
            # Button to fetch Instagram data
            if not st.session_state.fetch_data_clicked:
                if st.button("Fetch Instagram Data"):
                    st.session_state.fetch_data_clicked = True
                    with st.spinner("Fetching Instagram data..."):
                        instagram_data = fetch_instagram_data(
                            st.session_state.instagram_username,
                            start_date
                        )
                        if instagram_data:
                            st.session_state.instagram_data = instagram_data

            # Display Instagram data if we have it
            if st.session_state.instagram_data:
                st.json(st.session_state.instagram_data)

            # Add a reset button to start over
            if st.button("Reset Instagram Search"):
                st.session_state.instagram_search_clicked = False
                st.session_state.fetch_data_clicked = False
                st.session_state.instagram_username = None
                st.session_state.instagram_data = None
                st.session_state.instagram_response = None
                st.rerun()

    elif platform == "Facebook":
        st.info(f"Searching Facebook for posts about {company} from {start_date} to {end_date}...")
    else:
        st.error(f"Incompatible platform: {platform}. Please choose Instagram or Facebook.")