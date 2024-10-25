import assemblyai as aai
"b82693154c7a4a7ca95675dd807a3fe7"

class Audio:

    def __init__(self,apikey,audiofile):

        aai.settings.api_key = apikey

        self.audio_file = audiofile

        self.config = aai.TranscriptionConfig(speech_model=aai.SpeechModel.nano, language_code="en_us")

        self.transcriber = aai.Transcriber(config=self.config)

    def transcribe(self):
        transcript = self.transcriber.transcribe(self.audio_file)

        if transcript.status == aai.TranscriptStatus.error:
            print(transcript.error)
        else:
            return transcript.text
            #with open("transcript.txt", "w") as file:
            #    print(transcript.text, file = file)



