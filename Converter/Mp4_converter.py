import tempfile
from moviepy.editor import VideoFileClip
import io

class VideoConverter:
    def __init__(self, video_file):
        # Create a temporary file to store the uploaded video
        self.temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp4")
        self.temp_file.write(video_file.read())  # Write video content to temp file
        self.temp_file.seek(0)  # Reset file pointer to the beginning
        self.video = VideoFileClip(self.temp_file.name)

    def convert_to_mp3(self):
        # Create a temporary file for the MP3 output
        temp_mp3_file = tempfile.NamedTemporaryFile(delete=False, suffix=".mp3")
        
        # Write the audio to the temporary MP3 file
        self.video.audio.write_audiofile(temp_mp3_file.name)
        
        # Read the MP3 file content into a BytesIO buffer
        with open(temp_mp3_file.name, "rb") as f:
            mp3_buffer = io.BytesIO(f.read())
        
        # Clean up temporary MP3 file
        temp_mp3_file.close()

        # Reset buffer position to the start
        mp3_buffer.seek(0)
        return mp3_buffer

    def __del__(self):
        # Clean up the temporary video file
        self.temp_file.close()
