import streamlit as st
import warnings
import sys
import re
import clipboard

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

# Initialize session state for API key
if 'api_key' not in st.session_state:
    st.session_state.api_key = ""
    st.session_state.youtube = None

if 'copy_success' not in st.session_state:
    st.session_state.copy_success = False

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

st.sidebar.header("Enter YouTube Link")
youtube_link = st.sidebar.text_input("Link")
load_button = st.sidebar.button("Load")


if load_button and youtube_link:
    # Check if API key is provided
    if not st.session_state.api_key:
        st.error("Please enter your YouTube API Key in the sidebar to continue")
    else:
        video_id = extract_video_id(youtube_link)
        if video_id:
            st.sidebar.write("Video ID:", video_id)

            # Fetch comments once
            comments = fetch_video_comments(video_id)

            # Generate CSV and TXT content in memory
            csv_content = generate_csv_content(comments)
            txt_content = generate_txt_content(comments)

            st.sidebar.button("Copy to Clipboard", on_click=lambda: clipboard.copy(txt_content))

            # Create download buttons
            col1, col2 = st.sidebar.columns(2)
            with col1:
                st.download_button(
                    label="Download CSV",
                    data=csv_content.encode('utf-8'),
                    file_name=f"{video_id}.csv",
                    mime="text/csv"
                )
            with col2:
                st.download_button(
                    label="Download Text",
                    data=txt_content.encode('utf-8'),
                    file_name=f"{video_id}.txt",
                    mime="text/plain"
                )

            # Get video details including title and statistics
            video_details = get_video_details(video_id)

            if video_details:
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
            _, video_container, _ = st.columns([10, 80, 10])
            video_container.video(data=youtube_link)

            # Add a section for comments
            st.markdown("### Comments")


            # Display comments in a read-only text area
            st.text_area(
                label="",
                value=txt_content,
                height=400,
                key="comments-text-area",
                disabled=False,  # Make it selectable but read-only looking
                label_visibility="collapsed"
            )
elif load_button and not youtube_link:
    st.error("Please enter a YouTube link")
else:
    st.info("Enter a YouTube link and click 'Load' to view video information and download comments")

# if st.session_state.copy_success:
#     st.toast(f"Copied to clipboard!", icon='✅' )
#     st.session_state.copy_success = False
