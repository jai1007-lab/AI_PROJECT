import os
from groq import Groq

class QuizLLM:
    def __init__(self, apikey, text, num_questions=5):
        self.client = Groq(api_key=apikey)
        self.transcription_text = text
        self.num_questions = num_questions
        self.prompt()

    def prompt(self):
        # Construct the file path for the prompt file
        script_dir = os.path.dirname(os.path.abspath(__file__))
        prompt_file_path = os.path.join(script_dir, 'prompt', 'quizzify-prompt.txt')

        try:
            with open(prompt_file_path, 'r') as file:
                self.prompt_text = file.read()
        except FileNotFoundError:
            raise FileNotFoundError(f"Prompt file not found: {prompt_file_path}")

    def generate_quiz(self):
        """
        Generate quiz questions using Groq API.
        """
        formatted_prompt = self.prompt_text.format(
            num_questions=self.num_questions,
            text=self.transcription_text
        )

        # Make the request to Groq's API
        chat_completion = self.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {"role": "user", "content": formatted_prompt}
            ],
            temperature=1,
            max_tokens=3000,
            top_p=1,
            stream=False,
            stop=None,
        )

        # Return generated quiz questions
        return chat_completion.choices[0].message.content
