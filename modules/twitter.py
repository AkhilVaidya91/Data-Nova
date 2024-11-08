from apify_client import ApifyClient
import pandas as pd
import re
import requests
import tempfile
import os
import google.generativeai as genai
from datetime import datetime, timedelta
from pymongo import MongoClient

MONGO_URI = os.getenv('MONGO_URI')
MONGO_URI = "mongodb+srv://akhilvaidya22:qN2dxc1cpwD64TeI@digital-nova.cbbsn.mongodb.net/?retryWrites=true&w=majority&appName=digital-nova"
client = MongoClient(MONGO_URI)
db = client['digital_nova']
output_files_collection = db['output_files']

# Function to get a caption for an image using the GenAI model
def get_post_text(post_url, api_key):
    genai.configure(api_key=api_key)
    response = requests.get(post_url)
    image_data = response.content

    # Create a unique temporary file for each request
    temp_dir = tempfile.mkdtemp()
    temp_file_path = os.path.join(temp_dir, f"temp_{os.getpid()}_{datetime.now().strftime('%Y%m%d%H%M%S%f')}.jpg")

    try:
        with open(temp_file_path, 'wb') as temp_file:
            temp_file.write(image_data)
        
        myfile = genai.upload_file(temp_file_path)
        model = genai.GenerativeModel("gemini-1.5-flash")
        result = model.generate_content(
            [myfile, "\n\n", "Write a caption for this image. make sure that the caption is descriptive and perfectly describes whatever the image is trying to convey to the viewer."],
            safety_settings=[
            {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
            {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"}
        ])
        return result.text

    except Exception as e:
        print(f"An error occurred: {e}")
        return None

    finally:
        # Clean up both the file and the temporary directory
        try:
            os.unlink(temp_file_path)
            os.rmdir(temp_dir)
        except OSError:
            pass

# Main function that accepts all inputs, including API keys
def run(apify_api_token, genai_api_key, company_name, num_accounts, accounts, num_queries, search_queries, since, until, tweets_desired, save_directory, username):
    
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
    filename = f"twitter_{company_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}_info.xlsx"
    # excel_filename = os.path.join(save_directory, filename)
    # df.to_excel(excel_filename, index=False)

    # Save the output file details to the MongoDB collection
    output_files_collection.insert_one({
        'username': username,
        'file_type': 'twitter',
        'filename': filename,
        # 'filepath': excel_filename,
        'timestamp': datetime.now(),
    })
    
    return df, filename