from apify_client import ApifyClient
import pandas as pd
import re
import requests
import tempfile
import os
import google.generativeai as genai

# Function to get a caption for an image using the GenAI model
def get_post_text(image_url, api_key, save_directory):
    genai.configure(api_key=api_key)
    
    # Download the image from the URL
    response = requests.get(image_url)
    image_data = response.content

    # Write the image to a temporary file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg", dir=save_directory) as temp_file:
        temp_file.write(image_data)
        temp_file_path = temp_file.name

    try:
        # Upload the image and get a caption
        myfile = genai.upload_file(temp_file_path)
        model = genai.GenerativeModel("gemini-1.5-flash")
        result = model.generate_content(
            [myfile, "\n\n", "Write a caption for this image. Make sure the caption is descriptive and perfectly describes what the image conveys."],
            safety_settings=[
                {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"}
            ]
        )
        
        # Return the caption text
        return result.text
    finally:
        # Ensure the temporary file is deleted
        os.unlink(temp_file_path)

# Main function that accepts all inputs, including API keys
def run(apify_api_token, genai_api_key, company_name, num_accounts, accounts, num_queries, search_queries, since, until, tweets_desired, save_directory):
    
    # Initialize the ApifyClient with the provided API token
    client = ApifyClient(apify_api_token)

    # Create the directory if it doesn't exist
    if not os.path.exists(save_directory):
        os.makedirs(save_directory)

    # Prepare the Actor input (for retrieving tweet URLs)
    run_input = {
        "searchQueries": search_queries,
        "tweetsDesired": tweets_desired,
        "includeUserInfo": True,
        "fromTheseAccounts": accounts,
        "proxyConfig": {
            "useApifyProxy": True,
            "apifyProxyGroups": ["RESIDENTIAL"],
        },
        "since": since,
        "until": until,
    }

    # Run the Actor and wait for it to finish
    run = client.actor("2s3kSMq7tpuC3bI6M").call(run_input=run_input)

    # Initialize an empty list to store tweet data
    tweets_data = []

    # Fetch and process Actor results
    for item in client.dataset(run["defaultDatasetId"]).iterate_items():
        tweet_url = item['url']  # Get the tweet URL
        
        # Extract user details from the tweet data
        user_info = item.get('user', {})
        
        # Process images: remove the first 23 characters from each image URL
        images_array = [img[23:] for img in item.get('images', [])]
        
        # Initialize an empty list to store captions for each image
        captions = []
        
        # Generate captions for each image and save them in the specified directory
        for img_url in images_array:
            caption = get_post_text(img_url, genai_api_key, save_directory)
            captions.append(caption)
        
        # Append tweet details along with user data and image captions to the list
        tweets_data.append({
            'id': item['id'],
            'url': tweet_url,
            'images': images_array,  # Store image URLs as an array
            'captions': captions,  # Store the captions for each image
            'isQuote': item['isQuote'],
            'isReply': item['isReply'],
            'isRetweet': item['isRetweet'],
            'likes': item['likes'],
            'replies': item['replies'],
            'text': item['text'],
            'hashtags': ', '.join(re.findall(r"#(\w+)", item['text'])),  # Extract hashtags
            # User details
            'user_username': user_info.get('username', ''),
            'user_full_name': user_info.get('userFullName', ''),
            'user_description': user_info.get('description', ''),
            'user_verified': user_info.get('verified', False),
            'user_total_tweets': user_info.get('totalTweets', 0),
            'user_total_likes': user_info.get('totalLikes', 0),
            'user_total_followers': user_info.get('totalFollowers', 0),
            'user_total_following': user_info.get('totalFollowing', 0),
            'user_joined': user_info.get('joinDate', ''),
        })

    # Convert the list of tweet data to a DataFrame
    df = pd.DataFrame(tweets_data)

    # Save the DataFrame to an Excel file in the specified directory
    filename = f"{company_name}_twitter.xlsx"
    excel_filename = os.path.join(save_directory, f"{company_name}_twitter.xlsx")
    df.to_excel(excel_filename, index=False)
    
    return df, filename

# apify_api_token = input("Enter your Apify API token: ")
# genai_api_key = input("Enter your GenAI API key: ")
# company_name = input("Enter the company name: ")
# # num_accounts = int(input("Enter the number of Twitter accounts: "))
# accounts = [input(f"Enter account {i+1} username: ") for i in range(num_accounts)]
# num_queries = int(input("Enter the number of search queries: "))
# search_queries = [input(f"Enter search query {i+1}: ") for i in range(num_queries)]
# since = input("Enter the 'since' date (YYYY-MM-DD): ")
# until = input("Enter the 'until' date (YYYY-MM-DD): ")
# tweets_desired = int(input("Enter the number of tweets desired: "))
# save_directory = input("Enter the directory where you want to save the files: ")

# # Call the run function
# run(apify_api_token, genai_api_key, company_name, num_accounts, accounts, num_queries, search_queries, since, until, tweets_desired, save_directory)