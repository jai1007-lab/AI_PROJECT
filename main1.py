import json
import re
import streamlit as st
from Audio.transcribe import Audio
from Summary.summary import LLM
from Converter.Mp4_converter import VideoConverter
from Converter.YT_converter import youtube_converter
from Converter.pdf_reader import PDFReader
from quizzify.core import QuizLLM

def clean_and_parse_quiz(raw_quiz):
    try:
        start_index = raw_quiz.find("[")
        end_index = raw_quiz.rfind("]")
        if start_index == -1 or end_index == -1:
            raise ValueError("No valid JSON array found in the response.")
        json_content = raw_quiz[start_index:end_index + 1]
        json_content = re.sub(r",\s*}(\s*)$", "}", json_content.strip())
        json_content = re.sub(r",\s*\](\s*)$", "]", json_content.strip())
        quiz_data = json.loads(json_content)
        return quiz_data
    except (ValueError, json.JSONDecodeError) as e:
        st.error(f"Failed to parse quiz data: {e}")
        return None

def display_quiz(quiz_data):
    if "current_question_index" not in st.session_state:
        st.session_state.current_question_index = 0

    question_index = st.session_state.current_question_index
    question_data = quiz_data[question_index]

    # Display the current question
    st.write(f"**Q{question_index + 1}/{len(quiz_data)}: {question_data['question']}**")
    choices = [opt["value"] for opt in question_data["choices"]]
    correct_key = question_data["answer"]
    explanation = question_data["explanation"]

    # Session key for answer persistence
    session_key = f"q{question_index}_selected"
    if session_key not in st.session_state:
        st.session_state[session_key] = None

    # Display radio options
    selected_option = st.radio("Choose your answer:", choices, key=session_key)

    # Submit button logic
    if "answer_feedback" not in st.session_state:
        st.session_state["answer_feedback"] = {}

    # Display feedback and explanation only if Submit is clicked
    if st.button("Submit", key=f"submit_q{question_index}"):
        correct_answer = next(
            (opt["value"] for opt in question_data["choices"] if opt["key"] == correct_key), None
        )
        feedback = "Correct!" if selected_option == correct_answer else f"Wrong! The correct answer is: {correct_answer}"
        st.session_state["answer_feedback"][question_index] = feedback

    feedback = st.session_state["answer_feedback"].get(question_index, None)
    if feedback:
        feedback = str(feedback)
        if "Correct" in feedback:
            st.success(feedback)
        else:
            st.error(feedback)
        st.write(f"**Explanation:** {explanation}")

    # Navigation buttons
    col1, col2 = st.columns(2)

    # Disable Previous button on the first question
    with col1:
        if question_index == 0:
            st.button("Previous", key=f"prev_{question_index}", disabled=True)
            st.warning("You are on the first question. No previous question.")
        else:
            if st.button("Previous", key=f"prev_{question_index}"):
                st.session_state.current_question_index -= 1
                st.session_state["answer_feedback"] = {}  # Clear feedback for navigation
                st.rerun()  # Force app to rerun immediately

    # Disable Next button on the last question
    with col2:
        if question_index == len(quiz_data) - 1:
            st.button("Next", key=f"next_{question_index}", disabled=True)
            st.warning("You are on the last question. No next question.")
        else:
            if st.button("Next", key=f"next_{question_index}"):
                st.session_state.current_question_index += 1
                st.session_state["answer_feedback"] = {}  # Clear feedback for navigation
                st.rerun()  # Force app to rerun immediately


def main():
    st.title("AI Summarization and Quiz Generation tool")

    option = st.radio("Choose file type:", ("MP3", "MP4", "YouTube URL", "PDF", "Text"))
    if "transcript" not in st.session_state:
        st.session_state.transcript = None

    if option == "MP4":
        uploaded_file = st.file_uploader("Choose an MP4 file", type=["mp4"])
        if uploaded_file:
            with st.spinner("Processing..."):
                video = VideoConverter(uploaded_file)
                audio_file = video.convert_to_mp3()
                audio = Audio("b82693154c7a4a7ca95675dd807a3fe7", audio_file)
                st.session_state.transcript = audio.transcribe()
    elif option == "MP3":
        uploaded_file = st.file_uploader("Choose an MP3 file", type=["mp3"])
        if uploaded_file:
            with st.spinner("Processing..."):
                audio = Audio("b82693154c7a4a7ca95675dd807a3fe7", uploaded_file)
                st.session_state.transcript = audio.transcribe()
    elif option == "YouTube URL":
        youtube_url = st.text_input("YouTube URL")
        if youtube_url:
            with st.spinner("Processing..."):
                yt_converter = youtube_converter(youtube_url)
                st.session_state.transcript = yt_converter.display_transcript()
    elif option == "PDF":
        uploaded_file = st.file_uploader("Choose a PDF file", type=["pdf"])
        if uploaded_file is not None:
            # Read PDF content
            with st.spinner("Reading PDF..."):
                pdf_reader = PDFReader(uploaded_file)
                st.session_state.transcript = pdf_reader.read_pdf_content(uploaded_file)
    elif option == "Text":
        st.header("Enter your text")
        text = st.text_area("Text", "")
        if text:
            # Run audio transcription function
            with st.spinner("Processing text..."):
                st.session_state.transcript = text

    if st.session_state.transcript:
        with st.expander("📜 Full Transcript"):
            st.text_area("Transcript", st.session_state.transcript, height=300)

        action = st.radio("What would you like to do?", ("Generate Summary", "Generate Quiz"))
        if action == "Generate Summary":
            #st.button("Generate Summary")
            if st.button("Generate Summary"):
                with st.spinner("Generating summary..."):
                    llm = LLM("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", st.session_state.transcript)
                    summary = llm.generate_summary()
                    with st.expander("📜 Summary"):
                        st.write(summary)

        elif action == "Generate Quiz":
            num_questions = st.slider("Number of quiz questions:", 1, 10, 5)
            if st.button("Generate Quiz"):
                with st.spinner("Generating quiz..."):
                    quiz_llm = QuizLLM("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", st.session_state.transcript, num_questions)
                    raw_quiz = quiz_llm.generate_quiz()
                    st.write("Raw Output from LLM:",raw_quiz)
                    quiz_data = clean_and_parse_quiz(raw_quiz)
                    st.write("Cleaned response", quiz_data)
                    if quiz_data:
                        st.session_state.quiz_data = quiz_data
                    else:
                        st.error("Quiz generation failed.")

            if "quiz_data" in st.session_state:
                display_quiz(st.session_state.quiz_data)

if __name__ == "__main__":
    main()
