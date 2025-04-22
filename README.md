# YouTube Comments Downloader 💬

This project provides a web application for downloading YouTube comments. It allows users to input a YouTube link and retrieves the comments associated with that video. The application also displays video information and channel information.

## Features ✨

- Extracts the video ID from a YouTube link.
- Retrieves comments from the specified YouTube video and saves them to a CSV file. 💬📑
- Retrieves video and channel information from the YouTube API. 📺🔍
- Provides an interactive web interface using Streamlit. 🌐✨
- Allows downloading the comments as a CSV file. 📥

## Installation 🛠️

1. Clone the repository:

   ```
   git clone https://github.com/yourusername/youtube-comment-sentimental-analysis.git
   cd youtube-comment-sentimental-analysis
   ```

2. Set up Python 3.12 environment:

   ```
   # Using pyenv
   pyenv install 3.12.2
   pyenv local 3.12.2
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install the required dependencies:

   ```
   pip install -r requirements.txt
   ```

4. Obtain a YouTube Data API key from the [Google Cloud Console](https://console.cloud.google.com/).

5. Run the application using the compatibility script:

   ```
   python run.py
   ```

   Or directly with Streamlit:

   ```
   streamlit run app.py
   ```

## Usage 🚀

1. Open the application in your web browser.

2. Enter your YouTube Data API key in the sidebar. The key will be securely stored in your browser session. 🔑

3. Enter a valid YouTube link in the sidebar. 🔗

4. Wait for the application to retrieve the video and channel information, save the comments to a CSV file, and display the results. ⌛

5. Explore the video information and channel information. 📺

6. Download the comments as a CSV file using the download button in the sidebar. 📥

## Contributing 🤝

Contributions are welcome! If you find any issues or have suggestions for improvements, please open an issue or submit a pull request.

## License 📄

This project is licensed under the [MIT License](LICENSE).
