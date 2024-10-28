import streamlit as st
from Audio.transcribe import Audio
from Summary.summary import LLM
from Converter.Mp4_converter import VideoConverter
from Converter.YT_converter import youtube_converter
from quizzify.core import QuizLLM

def main():
    st.title("Audio Transcription, Summarization, and Quiz Generation")

    # Step 1: Choose file type (MP3, MP4, or YouTube URL)
    option = st.radio("Choose file type:", ("MP3", "MP4", "YouTube URL"))
    transcript = None  # Initialize transcript variable

    # Step 2: File uploading or URL input
    if option == "MP4":
        st.header("Upload your MP4 File")
        uploaded_file = st.file_uploader("Choose an MP4 file", type=["mp4"])

        if uploaded_file is not None:
            with st.spinner("Converting MP4 to MP3..."):
                video = VideoConverter(uploaded_file)
                audio_file = video.convert_to_mp3()

            with st.spinner("Transcribing audio..."):
                audio = Audio("b82693154c7a4a7ca95675dd807a3fe7", audio_file)
                transcript = audio.transcribe()

    elif option == "MP3":
        st.header("Upload your MP3 File")
        uploaded_file = st.file_uploader("Choose an MP3 file", type=["mp3"])

        if uploaded_file is not None:
            with st.spinner("Transcribing audio..."):
                audio = Audio("b82693154c7a4a7ca95675dd807a3fe7", uploaded_file)
                transcript = audio.transcribe()

    elif option == "YouTube URL":
        st.header("Enter the YouTube URL")
        youtube_url = st.text_input("YouTube URL", "")

        if youtube_url:
            with st.spinner("Fetching YouTube Transcript..."):
                yt_converter = youtube_converter(youtube_url)
                transcript = yt_converter.display_transcript()

    # Step 3: Display transcript and choose next action
    if transcript:
        st.write("**Transcript:**")
        st.text_area("Transcript", transcript, height=200)

        action = st.radio("What would you like to do?", ("Generate Summary", "Generate Quiz"))

        if action == "Generate Summary":
            with st.spinner("Generating summary..."):
                llm = LLM("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", transcript)
                summary = llm.generate_summary()
                st.write("**Summary:**")
                st.write(summary)

        elif action == "Generate Quiz":
            num_questions = st.slider("Select the number of quiz questions:", 1, 10, 5)

            if st.button("Generate Quiz"):
                with st.spinner("Generating quiz..."):
                    quiz_llm = QuizLLM("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", transcript, num_questions)
                    quiz = quiz_llm.generate_quiz()

                    # Convert the quiz string to a list of questions (assuming it's JSON-like)
                    try:
                        quiz_data = eval(quiz)  # Ensure safe conversion from string to list of dicts
                    except Exception as e:
                        st.error("Failed to generate a valid quiz.")
                        return

                    if quiz_data:
                        st.write("**Quiz:**")
                        # Iterate through each question in the quiz
                        for i, question_data in enumerate(quiz_data, start=1):
                            question = question_data.get('question', '')
                            options = question_data.get('choices', {})
                            correct_answer_key = question_data.get('answer', '')
                            explanation = question_data.get('explanation', '')

                            # Display the question
                            st.write(f"**Q{i}: {question}**")

                            # Display options as a radio button group
                            user_answer = st.radio(
                                f"Choose your answer for Q{i}:",
                                options=list(options.values()),
                                key=f"q{i}"
                            )

                            # Check if user has selected an option
                            if user_answer:
                                if user_answer == options.get(correct_answer_key, ''):
                                    st.success("Correct!")
                                else:
                                    st.error(f"Wrong! The correct answer is: {options.get(correct_answer_key, '')}")
                                
                                # Show explanation for the correct answer
                                st.write(f"**Explanation:** {explanation}")
                                st.write("---")  # Divider for readability

if __name__ == "__main__":
    main()
