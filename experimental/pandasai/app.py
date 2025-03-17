import streamlit as st
import pandas as pd
from pandasai import SmartDataframe
from pandasai.llm import OpenAI
import matplotlib
# Force matplotlib to use Agg backend
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import os
from dotenv import load_dotenv
import warnings

# Suppress numpy warnings about binary incompatibility
warnings.filterwarnings('ignore', message='numpy.dtype size changed')
warnings.filterwarnings('ignore', message='numpy.ufunc size changed')
# Suppress the PandasAI deprecation warning
warnings.filterwarnings('ignore', message='`PandasAI` .* is deprecated')

# Load environment variables from .env file (for API keys)
load_dotenv()

st.set_page_config(
    page_title="Chat with Your Dataframe",
    page_icon="📊",
    layout="wide"
)

# App title and description
st.title("💬 Chat with Your Dataframe")
st.markdown("""
Upload a CSV file and ask questions about your data in natural language.
The app will analyze your data and provide answers, including visualizations when appropriate.
""")

# Sidebar for API key input
with st.sidebar:
    st.header("Configuration")
    api_key = st.text_input("Enter your OpenAI API Key:", type="password")
    st.markdown("""
    ### Sample Questions to Ask:
    - What's the average value of [column]?
    - Show me the distribution of [column] as a histogram
    - Is there a correlation between [column1] and [column2]?
    - What are the top 5 values in [column]?
    - Plot [column1] against [column2]
    """)
    
    # Add in-app examples
    with st.expander("Sample Questions"):
        st.markdown("""
        Try asking questions like:
        - "What is the average of [column]?"
        - "Create a histogram of [column]"
        - "Plot a scatter plot of [column1] vs [column2]"
        - "Show me a bar chart of the top 5 [column]"
        - "Calculate the correlation between [column1] and [column2]"
        - "Summarize this dataset"
        
        Simply replace [column] with an actual column name from your data.
        """)
        
        # if uploaded_file is not None:
        #     st.markdown("### Columns in your data:")
        #     st.write(", ".join(df.columns.tolist()))

# Initialize session state for chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Function to initialize or reset SmartDataframe
def initialize_smart_dataframe(dataframe):
    if not api_key:
        st.warning("Please enter your OpenAI API key in the sidebar")
        return None
    
    # Initialize LLM
    llm = OpenAI(api_token=api_key)
    
    # Create SmartDataframe with explicit save_charts option
    smart_df = SmartDataframe(
        dataframe, 
        config={
            "llm": llm,
            "save_charts": True,  # Enable saving charts
            "verbose": True,  # More logging for troubleshooting
        }
    )
    return smart_df

# File uploader
uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

# Main content area
if uploaded_file is not None:
    # Read and display the dataframe
    df = pd.read_csv(uploaded_file)
    st.subheader("Your Data Preview:")
    st.dataframe(df.head())
    
    # Get column info for context
    col_info = df.dtypes.to_dict()
    col_info_str = "\n".join([f"- {col}: {dtype}" for col, dtype in col_info.items()])
    
    # Initialize SmartDataframe
    smart_df = initialize_smart_dataframe(df)
    
    # Display chat messages
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])
    
    # Chat input
    if prompt := st.chat_input("Ask a question about your data..."):
        # Add user message to chat history
        st.session_state.messages.append({"role": "user", "content": prompt})
        
        # Display user message
        with st.chat_message("user"):
            st.markdown(prompt)
        
        # Display assistant response
        with st.chat_message("assistant"):
            if smart_df:
                message_placeholder = st.empty()
                message_placeholder.markdown("Analyzing your data...")
                
                # Clear previous matplotlib plots to avoid conflicts
                plt.close('all')
                
                try:
                    # Get response from SmartDataframe
                    with st.spinner("Generating response..."):
                        response = smart_df.chat(prompt)
                        
                        # If the response is a direct figure from matplotlib
                        if plt.get_fignums():
                            st.pyplot(plt.gcf())
                            message_placeholder.markdown(str(response) if response else "Here's the visualization based on your query.")
                        # Check if the response has a figure attribute (some newer PandasAI versions)
                        elif hasattr(response, 'figure') and response.figure is not None:
                            st.pyplot(response.figure)
                            message_placeholder.markdown(response.answer if hasattr(response, 'answer') else str(response))
                        # For direct plots generated by PandasAI with _plot suffix
                        elif any(hasattr(smart_df, attr) and callable(getattr(smart_df, attr)) for attr in dir(smart_df) if attr.endswith('_plot')):
                            # The visualization might be handled by PandasAI internally
                            message_placeholder.markdown(str(response))
                            # Get the last generated figure if any
                            if plt.get_fignums():
                                st.pyplot(plt.gcf())
                        else:
                            # For text or tabular responses
                            message_placeholder.markdown(str(response))
                    
                    # Add assistant response to chat history
                    st.session_state.messages.append({"role": "assistant", "content": str(response)})
                
                except Exception as e:
                    message_placeholder.markdown(f"Error analyzing data: {str(e)}")
            else:
                st.markdown("Please enter an OpenAI API key in the sidebar to use this feature.")
else:
    # Instructions when no file is uploaded
    st.info("👆 Please upload a CSV file to get started!")
    
    # Example of how the app works
    with st.expander("How to use this app"):
        st.markdown("""
        1. Enter your OpenAI API key in the sidebar
        2. Upload a CSV file using the file uploader above
        3. Ask questions about your data in the chat input
        4. View visualizations and analysis results
        
        This app uses PandasAI to generate code for analyzing your data based on your questions,
        then executes that code to provide insights and visualizations.
        """)