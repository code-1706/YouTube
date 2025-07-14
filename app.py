import streamlit as st
import openai
import os
import re
import tempfile
import yt_dlp
from dotenv import load_dotenv

load_dotenv()

# Function to get API key from Streamlit secrets or environment
def get_openai_api_key():
    """Get OpenAI API key from Streamlit secrets or environment variables"""
    try:
        # Try Streamlit secrets first (for cloud deployment)
        return st.secrets["OPENAI_API_KEY"]
    except:
        # Fallback to environment variable
        return os.getenv("OPENAI_API_KEY")

st.set_page_config(
    page_title="YouTube Transcriber & Summarizer",
    page_icon="📺",
    layout="wide"
)

def extract_video_id(url):
    """Extract video ID from various YouTube URL formats"""
    patterns = [
        r'(?:youtube\.com/watch\?v=|youtu\.be/|youtube\.com/embed/)([^&\n?#]+)',
        r'youtube\.com/watch\?.*v=([^&\n?#]+)'
    ]
    
    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)
    
    return None

def extract_audio_from_youtube(url):
    """Extract audio from YouTube video using yt-dlp"""
    try:
        with tempfile.TemporaryDirectory() as temp_dir:
            audio_path = os.path.join(temp_dir, "audio.%(ext)s")
            
            ydl_opts = {
                'format': 'bestaudio[ext=m4a]/bestaudio/best',
                'outtmpl': audio_path,
                # Remove postprocessors since we don't have ffmpeg
                # We'll work with the original M4A format
                'quiet': True,
                'no_warnings': True,
                # Add user agent and other headers to avoid 403 errors
                'http_headers': {
                    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
                },
                # Try to avoid rate limiting
                'sleep_interval': 1,
                'max_sleep_interval': 5,
                # Use cookies if available
                'cookiefile': None,
                # Extract info first to check availability
                'extract_flat': False,
            }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                try:
                    # First, try to extract info to check if video is available
                    info = ydl.extract_info(url, download=False)
                    if not info:
                        raise Exception("Could not extract video information")
                    
                    # Now download the audio
                    ydl.download([url])
                except yt_dlp.utils.DownloadError as e:
                    raise Exception(f"Download failed: {str(e)}")
            
            # Find the actual audio file (yt-dlp might add extension)
            for file in os.listdir(temp_dir):
                if file.endswith(('.mp3', '.m4a', '.webm', '.opus')):
                    audio_file_path = os.path.join(temp_dir, file)
                    # Read the audio file and return its content
                    with open(audio_file_path, 'rb') as f:
                        return f.read()
            
            return None
    except Exception as e:
        st.error(f"Error extracting audio: {str(e)}")
        # Show more specific error message
        if "403" in str(e) or "Forbidden" in str(e):
            st.error("YouTube is blocking the download. This could be due to:")
            st.write("- Video is age-restricted or region-blocked")
            st.write("- YouTube's anti-bot measures")
            st.write("- Video requires sign-in")
            st.write("- Try a different video or check if the video is publicly accessible")
        return None

def transcribe_audio(audio_data):
    """Transcribe audio using OpenAI Whisper API"""
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Create a temporary file for the audio data
        # Use M4A format since that's what we're getting from YouTube
        with tempfile.NamedTemporaryFile(suffix='.m4a', delete=False) as temp_file:
            temp_file.write(audio_data)
            temp_file_path = temp_file.name
        
        try:
            # Open the temporary file for transcription
            with open(temp_file_path, 'rb') as audio_file:
                transcript = client.audio.transcriptions.create(
                    model="whisper-1",
                    file=audio_file,
                    response_format="text"
                )
            
            return transcript
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
            
    except Exception as e:
        st.error(f"Error transcribing audio: {str(e)}")
        return None

def summarize_text(text, max_length=500):
    """Summarize text using OpenAI GPT"""
    try:
        client = openai.OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        
        # Truncate text if too long (GPT has token limits)
        if len(text) > 15000:
            text = text[:15000] + "..."
        
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful assistant that summarizes YouTube video transcripts. Provide a concise summary with key points and main takeaways."},
                {"role": "user", "content": f"Please summarize this YouTube video transcript in about {max_length} words:\n\n{text}"}
            ],
            max_tokens=max_length + 100,
            temperature=0.7
        )
        
        return response.choices[0].message.content
    except Exception as e:
        return f"Error summarizing text: {str(e)}"

def main():
    st.title("📺 YouTube Transcriber & Summarizer")
    st.write("Enter a YouTube URL to extract audio, transcribe it using AI, and get an AI-powered summary.")
    
    # Sidebar for configuration
    with st.sidebar:
        st.header("⚙️ Configuration")
        
        # API Key input
        stored_api_key = get_openai_api_key()
        
        if stored_api_key:
            st.success("✅ OpenAI API Key configured")
            api_key = stored_api_key
        else:
            api_key = st.text_input("OpenAI API Key:", type="password", help="Enter your OpenAI API key")
            if api_key:
                os.environ["OPENAI_API_KEY"] = api_key
        
        # Summary length
        summary_length = st.slider("Summary Length (words):", 100, 1000, 300, 50)
        
        # Audio quality info
        st.info("🎵 **Audio Processing**\n\nThis app extracts audio from YouTube videos and transcribes it using OpenAI's Whisper model.")
    
    # Main content area
    col1, col2 = st.columns([3, 1])
    
    with col1:
        youtube_url = st.text_input(
            "YouTube URL:",
            placeholder="https://www.youtube.com/watch?v=...",
            help="Paste any YouTube URL here"
        )
    
    with col2:
        process_button = st.button("🚀 Process Video", type="primary", use_container_width=True)
    
    if process_button:
        if not youtube_url:
            st.error("Please enter a YouTube URL")
            return
        
        if not api_key and not get_openai_api_key():
            st.error("Please enter your OpenAI API Key in the sidebar")
            return
        
        # Extract video ID
        video_id = extract_video_id(youtube_url)
        if not video_id:
            st.error("Please enter a valid YouTube URL")
            return
        
        # Show video info
        st.subheader("📹 Video Information")
        st.write(f"**Video ID:** {video_id}")
        
        # Embed video (YouTube URLs work directly)
        try:
            st.video(youtube_url)
        except:
            st.write(f"**Video URL:** {youtube_url}")
            st.write("(Could not embed video preview)")
        
        # Process audio and transcription
        with st.spinner("🎵 Extracting audio from YouTube video..."):
            audio_data = extract_audio_from_youtube(youtube_url)
            
            if not audio_data:
                st.error("Could not extract audio from the video")
                st.info("💡 **Possible reasons:**")
                st.write("- Video is private or age-restricted")
                st.write("- Video has been deleted")
                st.write("- Network connection issues")
                st.write("- Video format not supported")
                return
        
        with st.spinner("🤖 Transcribing audio using OpenAI Whisper..."):
            transcript_text = transcribe_audio(audio_data)
            
            if not transcript_text:
                st.error("Could not transcribe audio")
                return
        
        # Generate summary
        with st.spinner("📝 Generating AI summary..."):
            summary = summarize_text(transcript_text, summary_length)
        
        # Display results
        st.success("✅ Processing complete!")
        
        # Create tabs for results
        tab1, tab2, tab3 = st.tabs(["📋 Summary", "📜 Full Transcript", "📊 Stats"])
        
        with tab1:
            st.subheader("AI Summary")
            st.write(summary)
            
            # Download summary
            st.download_button(
                label="📥 Download Summary",
                data=summary,
                file_name=f"youtube_summary_{video_id}.txt",
                mime="text/plain"
            )
        
        with tab2:
            st.subheader("Full Transcript")
            st.text_area("Transcript:", transcript_text, height=400)
            
            # Download transcript
            st.download_button(
                label="📥 Download Transcript",
                data=transcript_text,
                file_name=f"youtube_transcript_{video_id}.txt",
                mime="text/plain"
            )
        
        with tab3:
            st.subheader("Transcript Statistics")
            word_count = len(transcript_text.split())
            char_count = len(transcript_text)
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Words", f"{word_count:,}")
            with col2:
                st.metric("Characters", f"{char_count:,}")
            with col3:
                st.metric("Audio Source", "YouTube")
            
            # Show first few sentences
            st.subheader("Transcript Preview")
            sentences = transcript_text.split('. ')[:3]
            for i, sentence in enumerate(sentences, 1):
                st.write(f"**{i}.** {sentence.strip()}...")
    
    # Footer
    st.markdown("---")
    st.markdown("**Note:** This app extracts audio from YouTube videos and uses OpenAI's Whisper for transcription and GPT for summarization.")

if __name__ == "__main__":
    main()