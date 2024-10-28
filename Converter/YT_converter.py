from youtube_transcript_api import YouTubeTranscriptApi

class youtube_converter:
    @staticmethod
    def extract_video_id(url):
        # Extract the video ID from various possible YouTube URL formats
        if "youtu.be/" in url:
            return url.split('/')[-1]
        elif "v=" in url:
            return url.split("v=")[-1].split("&")[0]
        return None

    def __init__(self, url):
        self.video_id = self.extract_video_id(url)
        if self.video_id:
            try:
                self.transcript = YouTubeTranscriptApi.get_transcript(self.video_id)
            except Exception as e:
                print(f"Error retrieving transcript: {e}")
                self.transcript = []
        else:
            print("Invalid URL or video ID not found.")
            self.transcript = []

    def display_transcript(self):
        # Return the full transcript as a string
        if self.transcript:
            transcript_text = "".join([entry['text'] for entry in self.transcript])
            return transcript_text
        else:
            return "No transcript available."

# Example usage:
# url = "https://www.youtube.com/watch?v=5p248yoa3oE&t=89s"
# yt_converter = youtube_converter(url)
# print(yt_converter.display_transcript())
