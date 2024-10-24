import os
from groq import Groq


with open('../../Audio/transcriptions/transcript.txt', 'r') as file:
    transcription_text = file.read()

with open('../prompts/summary_prompt.txt', 'r') as file:
    prompt_text = file.read()

client = Groq(
    api_key=os.environ.get("GROQ_API_KEY"),
)

chat_completion = client.chat.completions.create(
    model="llama3-8b-8192",
    messages=[
        {
            "role": "user",
            "content": prompt_text
        },
        {
            "role": "user",
            "content": transcription_text
        }
    ],
    temperature=1,
    max_tokens=6000, # Let the users choose the length of the summary.
    top_p=1,
    stream=False,
    stop=None,
)

#print(chat_completion.choices[0].message.content)

# Implement the logic where each time the user asks for a summary, the code will generate a new summary and save it in a new file, summary[i].txt

with open("generated_summaries/summary1.txt", "w") as file:
        print(chat_completion.choices[0].message.content, file = file)
