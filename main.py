import streamlit as st
from Audio.transcribe import Audio
from LLM.summary import LLM

def main():
    st.title("Audio Transcription and Summarization")

    # MP3 File Upload
    st.header("Upload your MP3 File")
    uploaded_file = st.file_uploader("Choose an MP3 file", type=["mp3"])

    if uploaded_file is not None:
        # Run audio transcription function
        with st.spinner("Transcribing audio..."):
            audio = Audio("b82693154c7a4a7ca95675dd807a3fe7",uploaded_file)
            transcript = audio.transcribe()   

        # Display transcript in an expander (dropdown)
        with st.expander("📜 Full Transcript"):
            st.text_area("Transcript", transcript, height=300)

        # Run LLM summary function
        with st.spinner("Generating summary..."):
            llm = LLM("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",transcript)
            summary = llm.generate_summary()

        # Display summary in an expander (dropdown)
        with st.expander("📝 LLM-Generated Summary"):
            st.write(summary)

if __name__ == "__main__":
    main()
