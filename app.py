import streamlit as st
import warnings
import sys
import re
import clipboard
import time

# Filter deprecation warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

# Print Python version for debugging
print(f"Running Python {sys.version}", file=sys.stderr)

from YoutubeCommentScraper import fetch_video_comments, generate_csv_content, generate_txt_content, get_video_details
from googleapiclient.discovery import build

# Function to extract video ID from YouTube link
def extract_video_id(youtube_link):
    video_id_regex = r"^(?:https?:\/\/)?(?:www\.)?(?:youtube\.com\/watch\?v=|youtu\.be\/)([a-zA-Z0-9_-]{11})"
    match = re.search(video_id_regex, youtube_link)
    if match:
        video_id = match.group(1)
        return video_id
    else:
        return None

# Initialize session state variables
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
    st.session_state.youtube = None

if 'copy_success' not in st.session_state:
    st.session_state.copy_success = False

# Initialize session state for video ID only
if 'video_id' not in st.session_state:
    st.session_state.video_id = None

# Initialize session state for timestamp to prevent reloading
if 'last_loaded_time' not in st.session_state:
    st.session_state.last_loaded_time = None

st.set_page_config(page_title='YouTube Comments Downloader', page_icon = 'LOGO.png', initial_sidebar_state = 'auto')
#st.set_page_config(page_title=None, page_icon=None, layout="centered", initial_sidebar_state="auto", menu_items=None)
st.sidebar.title("YouTube Comments Downloader")

# API Key input with session state to remember previously entered key
st.sidebar.header("YouTube API Configuration")
api_key = st.sidebar.text_input(
    "Enter YouTube API Key",
    value=st.session_state.api_key,
    type="password",
    autocomplete="current-password",
    help="Your YouTube Data API v3 key from Google Cloud Console. It will be saved for your current session.",
    key="youtube_api_key",
    placeholder="Enter your API key here"
)
st.sidebar.caption("Your API key is stored securely in the session state and not shared.")

# Update session state when key changes
if api_key != st.session_state.api_key:
    st.session_state.api_key = api_key
    # Create YouTube client when key is provided
    if api_key:
        st.session_state.youtube = build('youtube', 'v3', developerKey=api_key)
    else:
        st.session_state.youtube = None

# Function to copy text content to clipboard
def copy_to_clipboard(txt_content):
    clipboard.copy(txt_content)
    st.session_state.copy_success = True

# Function to load video data
def load_video_data(youtube_link):
    if not st.session_state.api_key:
        st.error("Please enter your YouTube API Key in the sidebar to continue")
        return None, None, None, None

    video_id = extract_video_id(youtube_link)
    if not video_id:
        st.error("Invalid YouTube link")
        return None, None, None, None

    # Store video ID in session state and timestamp
    st.session_state.video_id = video_id
    st.session_state.last_loaded_time = time.time()

    # Fetch comments
    comments = fetch_video_comments(video_id)

    # Get video details
    video_details = get_video_details(video_id)

    # Generate content on demand
    csv_content = generate_csv_content(comments)
    txt_content = generate_txt_content(comments)

    return video_id, video_details, csv_content, txt_content

# Create a form for the YouTube link input
st.sidebar.header("Enter YouTube Link")
with st.sidebar.form(key="youtube_form"):
    youtube_link = st.text_input("Link")
    submit_button = st.form_submit_button(label="Load")

# Process the form submission
video_id = None
video_details = None
csv_content = None
txt_content = None

# Load data if form is submitted or if we already have a video ID
if submit_button and youtube_link:
    video_id, video_details, csv_content, txt_content = load_video_data(youtube_link)
    if video_id:
        st.sidebar.write("Video ID:", video_id)
elif st.session_state.video_id:
    # We have a video ID from a previous load, display it
    video_id = st.session_state.video_id
    st.sidebar.write("Video ID:", video_id)

    # Fetch data again (this won't trigger a reload since we're not in a callback)
    comments = fetch_video_comments(video_id)
    video_details = get_video_details(video_id)
    csv_content = generate_csv_content(comments)
    txt_content = generate_txt_content(comments)

# Create a container for the sidebar buttons
sidebar_button_container = st.sidebar.container()

# Display copy and download buttons if content is available
if video_id and txt_content and csv_content:
    with sidebar_button_container:
        st.button(
            "Copy to Clipboard",
            key="copy_button",
            on_click=copy_to_clipboard,
            args=(txt_content,)
        )

        # Create download buttons
        col1, col2 = st.columns(2)
        with col1:
            st.download_button(
                label="Download CSV",
                data=csv_content.encode('utf-8'),
                file_name=f"{video_id}.csv",
                mime="text/csv",
                key=f"csv_download_{video_id}"
            )
        with col2:
            st.download_button(
                label="Download Text",
                data=txt_content.encode('utf-8'),
                file_name=f"{video_id}.txt",
                mime="text/plain",
                key=f"txt_download_{video_id}"
            )

# Create a container for the main content
main_content = st.container()

# Display video details if available
if video_details:
    with main_content:
        # Display video title
        st.header(video_details['title'])

        # Format numbers with commas for better readability
        stats = video_details['statistics']
        view_count = f"{int(stats.get('viewCount', 0)):,}"
        like_count = f"{int(stats.get('likeCount', 0)):,}"
        comment_count = f"{int(stats.get('commentCount', 0)):,}"

        # Stats display
        cols = st.columns(3)

        with cols[0]:
            st.metric("Views", view_count)

        with cols[1]:
            st.metric("Likes", like_count)

        with cols[2]:
            st.metric("Comments", comment_count)

        # Display the video
        youtube_video_url = f"https://www.youtube.com/watch?v={video_id}"
        _, video_container, _ = st.columns([10, 80, 10])
        video_container.video(data=youtube_video_url)

        # Add a section for comments
        st.markdown("### Comments")

        # Display comments in a read-only text area
        if txt_content:
            st.text_area(
                label="",
                value=txt_content,
                height=400,
                key=f"comments-text-area-{video_id}",
                disabled=False,  # Make it selectable but read-only looking
                label_visibility="collapsed"
            )
elif submit_button and not youtube_link:
    st.error("Please enter a YouTube link")
elif not st.session_state.video_id:
    st.info("Enter a YouTube link and click 'Load' to view video information and download comments")

# Show toast notification when copy is successful
if st.session_state.copy_success:
    st.toast("Copied to clipboard!", icon='✅')
    st.session_state.copy_success = False
