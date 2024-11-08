from googleapiclient.discovery import build
import pandas as pd
import openpyxl
import requests
import os
from io import BytesIO
from PIL import Image as PilImage
from openpyxl.drawing.image import Image
import tempfile
import google.generativeai as genai
from datetime import datetime
from youtube_transcript_api import YouTubeTranscriptApi, NoTranscriptFound, TranscriptsDisabled, VideoUnavailable
from pymongo import MongoClient


# api_key = os.getenv('YT_API_KEY')
youtube_api_key = None
MONGO_URI = os.getenv('MONGO_URI')
MONGO_URI = "mongodb+srv://akhilvaidya22:qN2dxc1cpwD64TeI@digital-nova.cbbsn.mongodb.net/?retryWrites=true&w=majority&appName=digital-nova"
client = MongoClient(MONGO_URI)
db = client['digital_nova']
output_files_collection = db['output_files']

def set_api_key(api_key):
    global youtube_api_key
    youtube_api_key = api_key

def get_channel_id(channel_name, youtube_api_key):
    url = f"https://www.googleapis.com/youtube/v3/search?part=snippet&type=channel&q={channel_name}&key={youtube_api_key}"
    
    response = requests.get(url)
    data = response.json()

    if 'items' in data and len(data['items']) > 0:
        channel_id = data['items'][0]['id']['channelId']
        return channel_id
    else:
        return None
    
def get_uploads_playlist_id(channel_id):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=contentDetails&id={channel_id}&key={youtube_api_key}"
    response = requests.get(url)
    data = response.json()
    
    if 'items' in data and len(data['items']) > 0:
        uploads_playlist_id = data['items'][0]['contentDetails']['relatedPlaylists']['uploads']
        return uploads_playlist_id
    else:
        return None
    
def get_video_ids_from_playlist(playlist_id, max_videos):
    video_ids = []
    url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={playlist_id}&maxResults=50&key={youtube_api_key}"
    
    while url and len(video_ids) < max_videos:
        response = requests.get(url)
        data = response.json()
        
        if 'items' in data:
            for item in data['items']:
                video_ids.append(item['contentDetails']['videoId'])
                
                # Stop when we have enough videos
                if len(video_ids) >= max_videos:
                    break
        
        # Handle pagination (next page token)
        url = f"https://www.googleapis.com/youtube/v3/playlistItems?part=contentDetails&playlistId={playlist_id}&maxResults=50&pageToken={data.get('nextPageToken')}&key={youtube_api_key}" if 'nextPageToken' in data and len(video_ids) < max_videos else None
    
    return video_ids[:max_videos]

def get_available_transcript(video_id):
    try:
        transcript_list = YouTubeTranscriptApi.list_transcripts(video_id)

        # Try english, If English is not available, get the first available transcript and translate to english
        # try:
        #     transcript = transcript_list.find_transcript(['en'])
        # except NoTranscriptFound:
        #     transcript = next(iter(transcript_list._manually_created_transcripts.values() or transcript_list._generated_transcripts.values())).translate('en')
        
        # Get the first available transcript
        transcript = next(iter(transcript_list._manually_created_transcripts.values() or transcript_list._generated_transcripts.values()))
        transcript_data = transcript.fetch()
        transcript_text = ' '.join([t['text'] for t in transcript_data])
        return {
            'text': transcript_text,
            'language': transcript.language_code
        }
    except TranscriptsDisabled:
        return {
            'text': "Transcripts are disabled for this video",
            'language': "N/A"
        }
    except Exception as e:
        return {
            'text': f"Error retrieving transcript: {str(e)}",
            'language': "N/A"
        }

def get_post_text(post_url, api_key):
    genai.configure(api_key=api_key)
    response = requests.get(post_url)
    image_data = response.content

    with tempfile.NamedTemporaryFile(delete=False, suffix=".jpg") as temp_file:
        temp_file.write(image_data)
        temp_file_path = temp_file.name

    try:
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
        os.unlink(temp_file_path)
        return result.text
    except Exception as e:
        os.unlink(temp_file_path)
        print(f"An error occurred: {e}")
        return None
    

def get_video_details(video_ids,max_comments):
    video_data = []
    for i in range(0, len(video_ids), 50):
        url = f"https://www.googleapis.com/youtube/v3/videos?part=snippet,statistics,contentDetails&id={','.join(video_ids[i:i+50])}&key={youtube_api_key}"
        response = requests.get(url)
        data = response.json()

        if 'items' in data:
            for video in data['items']:
                # thumbnail_url = video['snippet']['thumbnails']['high']['url']
                # thumbnail_text = get_post_text(thumbnail_url, api_key)
                video_info = {
                    'Video ID': video['id'],
                    'Title': video['snippet']['title'],
                    'Published At': video['snippet']['publishedAt'],
                    'Views': video['statistics'].get('viewCount', 'N/A'),
                    'Likes': video['statistics'].get('likeCount', 'N/A'),
                    'Comments': video['statistics'].get('commentCount', 'N/A'),
                    'Duration': video['contentDetails']['duration'],
                    'Tags': video['snippet'].get('tags', 'N/A'),
                    # 'Thumbnail': video['snippet']['thumbnails']['high']['url']
                }
                
                
                transcript_info = get_available_transcript(video['id'])
                video_info['Transcript'] = transcript_info['text']
                video_info['Transcript Language'] = transcript_info['language']
                video_data.append(video_info)
    
    return video_data

# Function to get top 5 comments of a video
def get_video_comments(video_id, max_comments):
    url = f"https://www.googleapis.com/youtube/v3/commentThreads?part=snippet&videoId={video_id}&maxResults={max_comments}&key={youtube_api_key}"
    response = requests.get(url)
    data = response.json()

    comments = []
    if 'items' in data:
        for item in data['items']:
            comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
            comments.append(comment)
    
    return comments

def download_thumbnail_image(url, video_id):
    response = requests.get(url)
    if response.status_code == 200:
        img = PilImage.open(BytesIO(response.content))
        img_path = f"thumbnails/{video_id}.jpg"
        img.save(img_path)
        return img_path
    else:
        return None
    


def scrape_channel_videos_to_excel(channel_id, channel_name,max_vids,max_comments, output_folder_path, username, youtube_key):

    set_api_key(youtube_key)
    # Get the uploads playlist ID for the channel
    playlist_id = get_uploads_playlist_id(channel_id)
    
    if playlist_id is None:
        print(f"Could not find uploads playlist for channel {channel_name}")
        return
    
    # Get all video IDs from the playlist
    video_ids = get_video_ids_from_playlist(playlist_id,max_vids)
    
    if len(video_ids) == 0:
        print(f"No videos found for channel {channel_name}")
        return
    
    # Get video details
    video_details = get_video_details(video_ids,max_comments)
    
    # Create a DataFrame from the video details
    df = pd.DataFrame(video_details)
    
    # Create the Excel file to write video data
    file_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{channel_name}_videos.xlsx"
    # excel_filename = f"{output_folder_path}/{file_name}"
    # df.to_excel(excel_filename, index=False)

    # Save the file path to the database
    output_files_collection.insert_one({
        'username': username,
        'file_type': 'YouTube_channel_videos',
        'file_name': file_name,
        # 'file_path': excel_filename,
        'created_at': datetime.now()
    })


    return df, file_name

def get_channel_statistics(channel_id):
    url = f"https://www.googleapis.com/youtube/v3/channels?part=snippet,statistics&id={channel_id}&key={youtube_api_key}"
    response = requests.get(url)
    data = response.json()
    
    if 'items' in data and len(data['items']) > 0:
        channel_data = data['items'][0]
        
        # Extract relevant information
        channel_info = {
            'Channel Name': channel_data['snippet']['title'],
            'Channel ID': channel_data['id'],
            'Description': channel_data['snippet']['description'],
            'Published At': channel_data['snippet']['publishedAt'],
            'Subscribers': channel_data['statistics'].get('subscriberCount', 'N/A'),
            'Total Views': channel_data['statistics'].get('viewCount', 'N/A'),
            'Total Videos': channel_data['statistics'].get('videoCount', 'N/A'),
        }
        return channel_info
    else:
        print(f"No data found for channel ID: {channel_id}")
        return None

# Function to save the channel statistics to an Excel file
def save_channel_statistics_to_excel(channel_id, output_folder_path, username, youtube_key):

    set_api_key(youtube_key)
    # Get channel statistics
    channel_stats = get_channel_statistics(channel_id)
    
    if channel_stats is None:
        return
    
    # Convert the data to a pandas DataFrame
    df = pd.DataFrame([channel_stats])
    
    # Ensure the output folder exists
    if not os.path.exists(output_folder_path):
        os.makedirs(output_folder_path)

    # Define the Excel file path
    file_name = f"{datetime.now().strftime('%Y%m%d_%H%M%S')}_{channel_stats['Channel Name']}_statistics.xlsx"
    # save_path = os.path.join(output_folder_path, file_name)
    
    # Save the data to an Excel file
    # df.to_excel(save_path, index=False)

    # Save the file path to the database
    output_files_collection.insert_one({
        'username': username,
        'file_type': 'YouTube_channel_statistics',
        'file_name': file_name,
        # 'file_path': save_path,
        'created_at': datetime.now()
    })

    return df, file_name
