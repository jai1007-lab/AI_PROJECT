import os
from groq import Groq

class LLM:
     
    def __init__(self,apikey,text):
        self.client = Groq(
        api_key = apikey #"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" #os.environ.get("GROQ_API_KEY"),
        )
        self.transcription_text = text

        self.prompt()
          
    def prompt(self):
         with open('Summary/prompts/summary_prompt.txt', 'r') as file:
            self.prompt_text = file.read()

    #def transcript(self):
        #with open('../../Audio/transcriptions/transcript.txt', 'r') as file:
        #    self.transcription_text = file.read()

    def generate_summary(self):

        chat_completion = self.client.chat.completions.create(
            model="llama3-8b-8192",
            messages=[
                {
                    "role": "user",
                    "content": self.prompt_text
                },
                {
                    "role": "user",
                    "content": self.transcription_text
                }
            ],
            temperature=1,
            max_tokens=6000, # Let the users choose the length of the summary.
            top_p=1,
            stream=False,
            stop=None,
        )
        return chat_completion.choices[0].message.content

        # Implement the logic where each time the user asks for a summary, the code will generate a new summary and save it in a new file, summary[i].txt

        with open("generated_summaries/summary1.txt", "w") as file:
                print(chat_completion.choices[0].message.content, file = file)
