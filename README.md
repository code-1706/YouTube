# YouTube Transcriber & Summarizer

A simple web application that extracts transcripts from YouTube videos and generates AI-powered summaries using OpenAI's GPT.

## Features

- Extract transcripts directly from YouTube videos (no audio download required)
- AI-powered summarization using OpenAI GPT-3.5-turbo
- Support for multiple languages
- Adjustable summary length
- Download transcripts and summaries as text files
- Clean, user-friendly Streamlit interface
- Video embedding and statistics

## Requirements

- Python 3.7+
- OpenAI API key

## Installation

1. Clone this repository or download the files
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Set up your OpenAI API key:
   - Copy `.env.example` to `.env`:
     ```bash
     cp .env.example .env
     ```
   - Edit `.env` and add your OpenAI API key:
     ```
     OPENAI_API_KEY=your_actual_api_key_here
     ```

## Usage

1. Run the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. Open your browser and go to `http://localhost:8501`

3. Enter your OpenAI API key in the sidebar (if not set in .env)

4. Paste a YouTube URL and click "Process Video"

5. View the AI summary and full transcript

6. Download the results as text files

## How It Works

1. **URL Processing**: Extracts the video ID from various YouTube URL formats
2. **Transcript Extraction**: Uses `youtube-transcript-api` to get transcripts directly from YouTube
3. **AI Summarization**: Sends the transcript to OpenAI GPT-3.5-turbo for intelligent summarization
4. **Results Display**: Shows the summary, full transcript, and statistics in a clean interface

## Supported URL Formats

- `https://www.youtube.com/watch?v=VIDEO_ID`
- `https://youtu.be/VIDEO_ID`
- `https://www.youtube.com/embed/VIDEO_ID`

## Limitations

- Only works with videos that have transcripts available
- Cannot process private, age-restricted, or deleted videos
- Summary quality depends on transcript quality
- Long videos may be truncated due to OpenAI token limits

## Dependencies

- `streamlit`: Web interface
- `openai`: AI summarization
- `youtube-transcript-api`: Transcript extraction
- `python-dotenv`: Environment variable management

## Deployment

### Deploy to Streamlit Cloud (Recommended)

1. **Fork/Upload to GitHub**: Upload this project to a GitHub repository

2. **Visit Streamlit Cloud**: Go to [share.streamlit.io](https://share.streamlit.io)

3. **Deploy**: Click "New app" and connect your GitHub repository

4. **Configure Secrets**: In your Streamlit Cloud dashboard, go to app settings and add:
   ```
   OPENAI_API_KEY = "your_actual_openai_api_key"
   ```

5. **Deploy**: Your app will be live at `https://your-app-name.streamlit.app`

### Local Development with Environment Variables

Create a `.env` file:
```bash
cp .env.example .env
# Edit .env and add your API key
```

### Other Deployment Options

- **Heroku**: Add `setup.sh` and `Procfile` for Heroku deployment
- **Docker**: Create `Dockerfile` for containerized deployment
- **AWS/GCP/Azure**: Deploy using their respective container services

## License

MIT License