import streamlit as st
import os
import warnings
import sys
import re

# Filter deprecation warnings
warnings.filterwarnings('ignore', category=DeprecationWarning)
warnings.filterwarnings('ignore', category=FutureWarning)

# Print Python version for debugging
print(f"Running Python {sys.version}", file=sys.stderr)

from YoutubeCommentScrapper import save_video_comments_to_csv,get_channel_info,get_channel_id,get_video_stats
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


def delete_non_matching_csv_files(directory_path, video_id):
    for file_name in os.listdir(directory_path):
        if not file_name.endswith('.csv'):
            continue
        if file_name == f'{video_id}.csv':
            continue
        os.remove(os.path.join(directory_path, file_name))


st.set_page_config(page_title='YouTube Comments Downloader', page_icon = 'LOGO.png', initial_sidebar_state = 'auto')
#st.set_page_config(page_title=None, page_icon=None, layout="centered", initial_sidebar_state="auto", menu_items=None)
st.sidebar.title("YouTube Comments Downloader")

# API Key input with session state to remember previously entered key
st.sidebar.header("YouTube API Configuration")
api_key = st.sidebar.text_input(
    "Enter YouTube API Key",
    value=st.session_state.api_key,
    type="password",
    help="Your YouTube Data API v3 key from Google Cloud Console. It will be saved for your current session.",
    key="api_key_input",
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
directory_path = os.getcwd()
# hide_st_style = """
#             <style>
#             #MainMenu {visibility: hidden;}
#             footer {visibility: hidden;}
#             </style>
#             """
# st.markdown(hide_st_style, unsafe_allow_html=True)


if youtube_link:
    # Check if API key is provided
    if not st.session_state.api_key:
        st.error("Please enter your YouTube API Key in the sidebar to continue")
    else:
        video_id = extract_video_id(youtube_link)
        if video_id:
            youtube = st.session_state.youtube
            channel_id = get_channel_id(video_id)
            st.sidebar.write("The video ID is:", video_id)
            csv_file = save_video_comments_to_csv(video_id)
            delete_non_matching_csv_files(directory_path,video_id)
            st.sidebar.write("Comments saved to CSV!")
            st.sidebar.download_button(label="Download Comments", data=open(csv_file, 'rb').read(), file_name=os.path.basename(csv_file), mime="text/csv")

            #using fn
            channel_info = get_channel_info(youtube,channel_id)

        col1, col2 = st.columns(2)

        st.title(" ")
        col3, col4 ,col5 = st.columns(3)


        with col3:
           video_count=channel_info['video_count']
           st.header("  Total Videos  ")
           #st.subheader("Total Videos")
           st.subheader(video_count)

        with col4:
           channel_created_date= channel_info['channel_created_date']
           created_date = channel_created_date[:10]
           st.header("Channel Created ")
           st.subheader(created_date)

        with col5:

            st.header(" Subscriber_Count ")
            st.subheader(channel_info["subscriber_count"])

        st.title(" ")

        stats = get_video_stats(video_id)

        st.title("Video Information :")
        col6, col7 ,col8 = st.columns(3)


        with col6:
            st.header("  Total Views  ")
           #st.subheader("Total Videos")
            st.subheader(stats["viewCount"])

        with col7:
           st.header(" Like Count ")
           st.subheader(stats["likeCount"])


        with col8:

            st.header(" Comment Count ")
            st.subheader(stats["commentCount"])

        st.header(" ")


        _, container, _ = st.columns([10, 80, 10])
        container.video(data=youtube_link)

        st.subheader("Channel Description ")
        channel_description = channel_info['channel_description']
        st.write(channel_description)

else:
    st.error("Invalid YouTube link")