import yt_dlp
import whisper
import os
from urllib.parse import urlparse, parse_qs

class VideoCrawler:
    def __init__(self, output_dir):
        """Initialize VideoCrawler with book name"""
        self.output_dir = output_dir
        self.base_dir = f"{output_dir}/video"
        os.makedirs(self.base_dir, exist_ok=True)

    def get_video_id(self, url):
        """Extract video ID from YouTube or Bilibili URL"""
        parsed_url = urlparse(url)
        
        if 'youtube.com' in parsed_url.netloc or 'youtu.be' in parsed_url.netloc:
            if parsed_url.netloc == 'youtu.be':
                return 'ytb_' + parsed_url.path[1:]
            if 'watch' in parsed_url.path:
                return 'ytb_' + parse_qs(parsed_url.query)['v'][0]
        
        elif 'bilibili.com' in parsed_url.netloc:
            # Extract video ID from Bilibili URL
            # Assuming URL format: https://www.bilibili.com/video/BV1xx411c7mD
            if '/' == parsed_url.path[-1]:
                parsed_url.path = parsed_url.path[:-1]
            video_id = parsed_url.path.split('/')[-1]
            return f'bilibili_{video_id}'
        
        return None

    def download_audio(self, url, output_path):
        """Download video in mp4 format and extract audio to mp3"""
        # Remove .mp3 extension to avoid double extension
        temp_video_path = output_path.rsplit('.', 1)[0]
        
        # Configure options to download video and extract audio in one go
        ydl_opts = {
            'format': 'mp4' if 'bilibili.com' in url else 'mp4',
            'outtmpl': temp_video_path,
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
        }
        
        try:
            # Download video and extract audio
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Clean up the video file
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
            
            return True
        except Exception as e:
            print(f"Error downloading/converting audio: {e}")
            # Clean up any partial downloads
            if os.path.exists(temp_video_path):
                os.remove(temp_video_path)
            return False

    def transcribe_audio(self, audio_path):
        """Transcribe audio using Whisper model"""
        try:
            model = whisper.load_model("large-v3", device="cuda")
            # Load and preprocess audio with Chinese language
            result = model.transcribe(audio_path, language="zh")
            print(result["text"])
            
            return result["text"]
        except Exception as e:
            print(f"Error transcribing audio: {e}")
            return None

    def process_video_url(self, url):
        """Process a single video URL"""
        video_id = self.get_video_id(url)
        if not video_id:
            print(f"Could not extract video ID from URL: {url}")
            return
        
        audio_path = f"{self.base_dir}/{video_id}.mp3"
        text_path = f"{self.base_dir}/{video_id}.txt"
        
        if os.path.exists(audio_path):
            print(f"Audio file {audio_path} already exists, skipping download...")
        else:
            # Download audio
            print(f"Downloading audio from {url}...")
            if not self.download_audio(url, audio_path):
                return
        
        # Transcribe audio
        if os.path.exists(text_path):
            print(f"Text file {text_path} already exists, skipping transcription...")
            transcription = open(text_path, 'r', encoding='utf-8').read()
        else:
            print("Transcribing audio...")
            transcription = self.transcribe_audio(audio_path)
            
        if transcription:
            # Save transcription
            with open(text_path, 'w', encoding='utf-8') as f:
                f.write(transcription)
            print(f"Transcription saved to {text_path}")
        else:
            print("Transcription failed")

    def process_video_urls(self, url_file):
        """Process a list of video URLs"""
        
        with open(url_file, "r") as f:
            video_urls = f.readlines()
        video_urls = [url.strip() for url in video_urls]
        for url in video_urls:
            print(f"\nProcessing {url}")
            self.process_video_url(url)

# Example usage
if __name__ == "__main__":
    output_dir = "example_book"
    # video_urls = [
    #     # "https://www.youtube.com/watch?v=Ru0keaEM5qM",
    #     "https://www.bilibili.com/video/BV1V7BbYBEFV"
    # ]
    
    crawler = VideoCrawler(output_dir)
    crawler.process_video_urls("video_link.txt")
