import os
import json
from urllib.parse import urlparse, parse_qs
import autogen
from typing import Dict, List, Optional, Any, Union

# Define configuration
config_list = [
    {
        "model": "gpt-4",
        "api_key": os.environ.get("OPENAI_API_KEY"),
    }
]

# Create agents
user_proxy = autogen.UserProxyAgent(
    name="User",
    is_termination_msg=lambda x: x.get("content", "") and "TERMINATE" in x.get("content", ""),
    human_input_mode="NEVER",
    max_consecutive_auto_reply=10,
)

download_agent = autogen.AssistantAgent(
    name="DownloadAgent",
    llm_config={"config_list": config_list},
    system_message="You are an agent responsible for downloading videos and extracting audio. You handle both YouTube and Bilibili videos."
)

transcription_agent = autogen.AssistantAgent(
    name="TranscriptionAgent",
    llm_config={"config_list": config_list},
    system_message="You are an agent responsible for transcribing audio files to text using Whisper."
)

class VideoCrawlerSystem:
    def __init__(self, output_dir: str):
        """Initialize the VideoCrawler system with an output directory."""
        self.output_dir = output_dir
        self.base_dir = os.path.join(output_dir, "video")
        os.makedirs(self.base_dir, exist_ok=True)
        self.download_agent = download_agent
        self.transcription_agent = transcription_agent
        
    def process_video_urls(self, url_file: str):
        """Process a list of video URLs from a file."""
        with open(url_file, "r") as f:
            video_urls = [url.strip() for url in f.readlines()]
        
        for url in video_urls:
            print(f"\nProcessing {url}")
            self.process_video_url(url)
            
    def process_video_url(self, url: str):
        """Process a single video URL by downloading and transcribing."""
        video_id = self.extract_video_id(url)
        if not video_id:
            print(f"Could not extract video ID from URL: {url}")
            return
        
        audio_path = os.path.join(self.base_dir, f"{video_id}.mp3")
        text_path = os.path.join(self.base_dir, f"{video_id}.txt")
        
        # Check if audio file already exists
        if os.path.exists(audio_path):
            print(f"Audio file {audio_path} already exists, skipping download...")
        else:
            # Download audio using DownloadAgent
            download_result = self.download_audio(url, audio_path)
            if not download_result:
                return
        
        # Check if transcription file already exists
        if os.path.exists(text_path):
            print(f"Text file {text_path} already exists, skipping transcription...")
        else:
            # Transcribe audio using TranscriptionAgent
            transcription = self.transcribe_audio(audio_path)
            if transcription:
                with open(text_path, 'w', encoding='utf-8') as f:
                    f.write(transcription)
                print(f"Transcription saved to {text_path}")
            else:
                print("Transcription failed")
    
    @staticmethod
    def extract_video_id(url: str) -> Optional[str]:
        """Extract video ID from YouTube or Bilibili URL."""
        parsed_url = urlparse(url)
        
        if 'youtube.com' in parsed_url.netloc or 'youtu.be' in parsed_url.netloc:
            if parsed_url.netloc == 'youtu.be':
                return 'ytb_' + parsed_url.path[1:]
            if 'watch' in parsed_url.path:
                return 'ytb_' + parse_qs(parsed_url.query)['v'][0]
        
        elif 'bilibili.com' in parsed_url.netloc:
            # Remove trailing slash if present
            path = parsed_url.path
            if '/' == path[-1]:
                path = path[:-1]
            video_id = path.split('/')[-1]
            return f'bilibili_{video_id}'
        
        return None

    def download_audio(self, url: str, output_path: str) -> bool:
        """Download video and extract audio using the DownloadAgent."""
        download_task = {
            "task": "download_audio",
            "url": url,
            "output_path": output_path
        }
        
        # Use the UserProxyAgent to initiate the task with the DownloadAgent
        user_proxy.initiate_chat(
            self.download_agent,
            message=f"""
            Please download the audio from this URL: {url}
            Save it to: {output_path}
            Details: {json.dumps(download_task)}
            """
        )
        
        # Actual implementation would be handled by specialized functions
        # For demonstration, we're simulating the agent's work
        return self._execute_download(url, output_path)
    
    def _execute_download(self, url: str, output_path: str) -> bool:
        """Execute the actual download (implementation similar to your original code)."""
        temp_video_path = output_path.rsplit('.', 1)[0]
        
        try:
            # This would import and use the necessary libraries
            # For Bilibili: use lux
            # For YouTube: use yt-dlp
            if 'bilibili.com' in url:
                import subprocess
                temp_video_directory = os.path.dirname(temp_video_path)
                temp_video_name = os.path.basename(temp_video_path)
                
                # Download using lux
                cmd = ['lux', '-o', temp_video_directory, '-O', temp_video_name, url]
                subprocess.run(cmd, check=True)
                
                # Convert to mp3
                mp3_path = f"{temp_video_path}.mp3"
                subprocess.run([
                    'ffmpeg', '-i', f"{temp_video_path}.mp4",
                    '-vn', '-acodec', 'libmp3lame', '-q:a', '2',
                    mp3_path
                ], check=True)
                
                # Clean up
                if os.path.exists(f"{temp_video_path}.mp4"):
                    os.remove(f"{temp_video_path}.mp4")
            else:
                # Use yt-dlp for YouTube
                import yt_dlp
                ydl_opts = {
                    'format': 'mp4',
                    'outtmpl': temp_video_path,
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
                
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    ydl.download([url])
                
                if os.path.exists(temp_video_path):
                    os.remove(temp_video_path)
            
            return True
        except Exception as e:
            print(f"Error downloading/converting audio: {e}")
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
            return False

    def transcribe_audio(self, audio_path: str) -> Optional[str]:
        """Transcribe audio using the TranscriptionAgent."""
        transcription_task = {
            "task": "transcribe_audio",
            "audio_path": audio_path
        }
        
        # Use the UserProxyAgent to initiate the task with the TranscriptionAgent
        user_proxy.initiate_chat(
            self.transcription_agent,
            message=f"""
            Please transcribe this audio file: {audio_path}
            Details: {json.dumps(transcription_task)}
            """
        )
        
        # Actual implementation would be handled by specialized functions
        # For demonstration, we're simulating the agent's work
        return self._execute_transcription(audio_path)
    
    def _execute_transcription(self, audio_path: str) -> Optional[str]:
        """Execute the actual transcription (implementation similar to your original code)."""
        try:
            import whisper
            model = whisper.load_model("large-v3", device="cuda")
            # Load and preprocess audio with Chinese language
            result = model.transcribe(audio_path, language="zh")
            print(result["text"])
            
            return result["text"]
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return None

# Example usage
if __name__ == "__main__":
    output_dir = "example_book"
    crawler_system = VideoCrawlerSystem(output_dir)
    crawler_system.process_video_urls("video_link.txt")
