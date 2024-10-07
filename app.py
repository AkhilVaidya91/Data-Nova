import streamlit as st
import os
from modules import instagram, amazon_reviews, tripadvisor
import zipfile
import io

gemini_api_key = 'AIzaSyAjDT14MAn93D1xJMsBtHeaNThaFIYeLbs'
# apify_api_key = 'apify_api_eQL36WHTap9vl7eUsHIgjjcwWKqRL50NAMOS'
apify_api_key = 'apify_api_KVxCV4c7NI3aUMUCDW2Wv4GjCzTgZu4awEVM'
op_path = 'output'

# gemini_api_key = os.getenv('GEMINI_API_KEY')
# apify_api_key = os.getenv('APIFY_API_KEY')
# op_path = os.getenv('OP_PATH')

if not os.path.exists(op_path):
    os.makedirs(op_path)

def main():
    st.set_page_config(page_title="Data Nova", page_icon="📊")

    st.title("Data Nova")
    st.subheader("Transforming Big Data into Strategic Insights")

    platform = st.selectbox("Platform Selection", ["Instagram", "Amazon Product Reviews", "TripAdvisor reviews"])

    if platform == "Instagram":
        # num_accounts = st.number_input("Number of accounts", min_value=1, value=1)
        
        account_handles = []
        handle = st.text_input(f"Instagram account handle: ")
        account_handles.append(handle)
        
        time_frame = st.selectbox("Time Frame Selection (months)", [6, 12, 24])
        
        max_posts = st.number_input("Max Posts Per Month", min_value=1, value=5)
        
        if st.button("Analyze"):
            list_of_account_dataframes, list_of_posts_dataframes, acc_file, post_file = instagram.run(gemini_api_key, apify_api_key, account_handles, "b", max_posts, 1, 1, 1, time_frame, op_path)
            
            df = list_of_account_dataframes[0]
            df_posts = list_of_posts_dataframes[0]
            st.write("Instagram account profile details.")
            st.dataframe(df)
            st.write("Instagram account posts details.")
            st.dataframe(df_posts)
            acc_file_path = os.path.join(op_path, acc_file)
            post_file_path = os.path.join(op_path, post_file)
            zip_buffer = io.BytesIO()
            with zipfile.ZipFile(zip_buffer, 'w') as zipf:
                zipf.write(acc_file_path, os.path.basename(acc_file))
                zipf.write(post_file_path, os.path.basename(post_file))

            zip_buffer.seek(0)

            st.download_button(
                label="Download ZIP",
                data=zip_buffer,
                file_name="instagram_data.zip",
                mime="application/zip"
            )

    
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

if __name__ == "__main__":
    main()