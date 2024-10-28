import streamlit as st
from Audio.transcribe import Audio
from Summary.summary import LLM
from Converter.Mp4_converter import VideoConverter
from Converter.YT_converter import youtube_converter

def main():
    st.title("Audio Transcription and Summarization")

    option = st.radio("Choose file type:", ("MP3", "MP4", "YouTube URL"))

    transcript = None  # Initialize transcript variable

    if option == "MP4":
        st.header("Upload your MP4 File")
        uploaded_file = st.file_uploader("Choose an MP4 file", type=["mp4"])

        if uploaded_file is not None:
            # Convert MP4 to MP3 using the VideoConverter
            with st.spinner("Converting MP3..."):
                video = VideoConverter(uploaded_file)
                audio_file = video.convert_to_mp3()

            # Run audio transcription function
            with st.spinner("Transcribing audio..."):
                audio = Audio("b82693154c7a4a7ca95675dd807a3fe7", audio_file)
                transcript = audio.transcribe()

    elif option == "MP3":
        st.header("Upload your MP3 File")
        uploaded_file = st.file_uploader("Choose an MP3 file", type=["mp3"])

        if uploaded_file is not None:
            # Run audio transcription function
            with st.spinner("Transcribing audio..."):
                audio = Audio("b82693154c7a4a7ca95675dd807a3fe7", uploaded_file)
                transcript = audio.transcribe()

    elif option == "YouTube URL":
        st.header("Enter the YouTube URL")
        youtube_url = st.text_input("YouTube URL", "")
        if youtube_url:
            # Extract the video ID from the YouTube URL
            with st.spinner("Extracting video ID..."):
                yt_converter = youtube_converter(youtube_url)
                transcript = yt_converter.display_transcript()
            

    # Display the transcript and summary if available
    if transcript:
        with st.expander("📜 Full Transcript"):
            st.text_area("Transcript", transcript, height=300)
        
        #option = st.radio("Choose your task:", ("Generate Summary", "Generate Quiz"))    

        with st.spinner("Generating summary..."):
            llm = LLM("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", transcript)
            summary = llm.generate_summary()

        with st.expander("📝 LLM-Generated Summary"):
            st.write(summary)

if __name__ == "__main__":
    main()
