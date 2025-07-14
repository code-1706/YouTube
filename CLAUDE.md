# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a YouTube Transcriber & Summarizer web application built with Python and Streamlit. The application extracts transcripts from YouTube videos using the YouTube Transcript API and generates AI-powered summaries using OpenAI's GPT-3.5-turbo.

## Development Commands

- `pip install -r requirements.txt` - Install dependencies
- `streamlit run app.py` - Start the web application
- `cp .env.example .env` - Set up environment variables

## Architecture

- `app.py`: Main Streamlit application with UI and core functionality
- `requirements.txt`: Python dependencies
- `.env.example`: Environment variable template
- `README.md`: Project documentation

### Key Dependencies
- `streamlit`: Web UI framework
- `openai`: AI summarization via GPT-3.5-turbo
- `youtube-transcript-api`: Direct transcript extraction from YouTube
- `python-dotenv`: Environment variable management

### Main Functions
- `extract_video_id()`: Parses YouTube URLs to extract video IDs
- `get_youtube_transcript()`: Fetches transcripts using YouTube Transcript API
- `summarize_text()`: Generates summaries using OpenAI GPT

## Environment Variables

- `OPENAI_API_KEY`: Required for AI summarization functionality

## Notes

The application uses YouTube's built-in transcripts rather than downloading audio, making it more efficient and cost-effective. It handles multiple URL formats and provides error handling for videos without transcripts.