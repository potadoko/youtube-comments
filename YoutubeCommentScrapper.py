import csv
import os
import sys
import traceback
from googleapiclient.discovery import build
from collections import Counter
import streamlit as st
from googleapiclient.errors import HttpError

import warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)
warnings.filterwarnings('ignore', message='.*numpy.ndarray size changed.*')

# YouTube API configuration
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

# Initialize youtube client with None, will be built when key is available
youtube = None

#video_id=extract_video_id(youtube_link)

def get_channel_id(video_id):
    # Access youtube client from session state
    youtube = st.session_state.youtube
    response = youtube.videos().list(part='snippet', id=video_id).execute()
    channel_id = response['items'][0]['snippet']['channelId']
    return channel_id

#channel_id=get_channel_id(video_id)


def save_video_comments_to_csv(video_id):
    try:
        # Access youtube client from session state
        youtube = st.session_state.youtube

        # Retrieve comments for the specified video using the comments().list() method
        comments = []
        try:
            results = youtube.commentThreads().list(
                part='snippet',
                videoId=video_id,
                textFormat='plainText',
                maxResults=100  # Limit results per page
            ).execute()

            # Extract the text content of each comment and add it to the comments list
            page_count = 0
            max_pages = 10  # Limit number of pages to avoid hitting API limits

            while results and page_count < max_pages:
                for item in results['items']:
                    try:
                        comment = item['snippet']['topLevelComment']['snippet']['textDisplay']
                        username = item['snippet']['topLevelComment']['snippet']['authorDisplayName']
                        comments.append([username, comment])
                    except KeyError as e:
                        st.warning(f"Skipping comment due to missing data: {str(e)}")
                        continue

                page_count += 1
                if 'nextPageToken' in results and page_count < max_pages:
                    nextPage = results['nextPageToken']
                    results = youtube.commentThreads().list(
                        part='snippet',
                        videoId=video_id,
                        textFormat='plainText',
                        pageToken=nextPage,
                        maxResults=100
                    ).execute()
                else:
                    break
        except HttpError as e:
            st.error(f"YouTube API error: {str(e)}")
            if "quotaExceeded" in str(e):
                st.error("YouTube API quota exceeded. Please try again tomorrow or use a different API key.")

        # Save the comments to a CSV file with the video ID as the filename
        filename = video_id + '.csv'

        if not comments:
            st.warning("No comments were found or could be retrieved.")
            # Create empty file with headers
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Username','Comment'])
            return filename

        try:
            with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(['Username','Comment'])
                for comment in comments:
                    # Handle potential encoding issues
                    username = str(comment[0]).encode('utf-8', errors='replace').decode('utf-8')
                    comment_text = str(comment[1]).encode('utf-8', errors='replace').decode('utf-8')
                    writer.writerow([username, comment_text])
        except Exception as e:
            st.error(f"Error saving CSV file: {str(e)}")
            traceback.print_exc(file=sys.stderr)

        return filename
    except Exception as e:
        st.error(f"Unexpected error fetching comments: {str(e)}")
        traceback.print_exc(file=sys.stderr)

        # Create empty file with headers as fallback
        filename = video_id + '.csv'
        with open(filename, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Username','Comment'])
        return filename

def get_video_stats(video_id):
    try:
        # Access youtube client from session state
        youtube = st.session_state.youtube
        response = youtube.videos().list(
            part='statistics',
            id=video_id
        ).execute()

        return response['items'][0]['statistics']

    except HttpError as error:
        print(f'An error occurred: {error}')
        return None




def get_channel_info(youtube, channel_id):
    try:
        response = youtube.channels().list(
            part='snippet,statistics,brandingSettings',
            id=channel_id
        ).execute()

        channel_title = response['items'][0]['snippet']['title']
        video_count = response['items'][0]['statistics']['videoCount']
        channel_logo_url = response['items'][0]['snippet']['thumbnails']['high']['url']
        channel_created_date = response['items'][0]['snippet']['publishedAt']
        subscriber_count = response['items'][0]['statistics']['subscriberCount']
        channel_description = response['items'][0]['snippet']['description']


        channel_info = {
            'channel_title': channel_title,
            'video_count': video_count,
            'channel_logo_url': channel_logo_url,
            'channel_created_date': channel_created_date,
            'subscriber_count': subscriber_count,
            'channel_description': channel_description
        }

        return channel_info

    except HttpError as error:
        print(f'An error occurred: {error}')
        return None



