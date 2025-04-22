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



def fetch_video_comments(video_id):
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

        return comments
    except Exception as e:
        st.error(f"Unexpected error fetching comments: {str(e)}")
        traceback.print_exc(file=sys.stderr)
        return []

def generate_csv_content(comments):
    """Generate CSV content from comments without writing to a file"""
    import io

    if not comments:
        # Create a CSV with just headers
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Username','Comment'])
        return output.getvalue()

    try:
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Username','Comment'])

        for comment in comments:
            # Handle potential encoding issues
            username = str(comment[0]).encode('utf-8', errors='replace').decode('utf-8')
            comment_text = str(comment[1]).encode('utf-8', errors='replace').decode('utf-8')
            writer.writerow([username, comment_text])

        return output.getvalue()
    except Exception as e:
        st.error(f"Error generating CSV content: {str(e)}")
        traceback.print_exc(file=sys.stderr)

        # Return just headers as fallback
        output = io.StringIO()
        writer = csv.writer(output)
        writer.writerow(['Username','Comment'])
        return output.getvalue()

def get_video_details(video_id):
    try:
        # Access youtube client from session state
        youtube = st.session_state.youtube
        response = youtube.videos().list(
            part='snippet,statistics',
            id=video_id
        ).execute()

        if 'items' in response and len(response['items']) > 0:
            video_data = response['items'][0]
            return {
                'title': video_data['snippet']['title'],
                'statistics': video_data['statistics']
            }
        else:
            st.error("Could not retrieve video details")
            return None

    except HttpError as error:
        st.error(f'An error occurred: {error}')
        return None

# Keep this for backward compatibility
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


def generate_txt_content(comments):
    """Generate text content from comments without writing to a file"""
    if not comments:
        return "No comments found"

    try:
        content = ""
        for comment in comments:
            # Handle potential encoding issues
            username = str(comment[0]).encode('utf-8', errors='replace').decode('utf-8')
            comment_text = str(comment[1]).encode('utf-8', errors='replace').decode('utf-8')
            content += f"{username}: {comment_text}\n"
        return content
    except Exception as e:
        st.error(f"Error generating TXT content: {str(e)}")
        traceback.print_exc(file=sys.stderr)
        return "Error generating comments"
