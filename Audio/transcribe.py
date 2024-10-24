import assemblyai as aai

aai.settings.api_key = "b82693154c7a4a7ca95675dd807a3fe7"

audio_file = "recordings/AndrewNG.mp3"

config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.nano, language_code="en_us")

transcriber = aai.Transcriber(config=config)

transcript = transcriber.transcribe(audio_file)

if transcript.status == aai.TranscriptStatus.error:
    print(transcript.error)
else:
    with open("transcriptions/transcript.txt", "w") as file:
        print(transcript.text, file = file)



