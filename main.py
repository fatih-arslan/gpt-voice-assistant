import requests
import speech_recognition as sr
import openai
from gtts import gTTS
import playsound
import os
import whisper
import assemblyai as aai
import pyttsx3
import streamlit as st

# pytts engine config
engine = pyttsx3.init()
engine.setProperty("rate", 130)
engine.setProperty("voice", "HKEY_LOCAL_MACHINE\SOFTWARE\Microsoft\Speech\Voices\Tokens\MSTTS_V110_trTR_Tolga")

openai.api_key = "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"
aai.settings.api_key = "a39221861e8e4ee39772674a3359c29e"

# openai whisper model
model = whisper.load_model("base")

# transcription with SpeechRecognition library
def transcribe_audio_with_sr(audio_file_path, language_code="tr-TR"):
    if os.path.exists(audio_file_path):
        recognizer = sr.Recognizer()
        with sr.AudioFile(audio_file_path) as source:
            audio = recognizer.record(source)
            try:
                text = recognizer.recognize_google(audio, language=language_code)
                return text
            except sr.UnknownValueError:
                return ""
            except sr.RequestError as e:
                return ""

# transcription with assemblyai
def transcribe_audio_with_aai(audio_file_path, language_code = "tr"):
    if os.path.exists(audio_file_path):
        config = aai.TranscriptionConfig(punctuate=True, language_code=language_code)
        transcriber = aai.Transcriber(config=config)
        transcript = transcriber.transcribe("audio_file_path")
        return transcript

# transcription with openai whisper
def transcribe_audio_with_whisper(audio_file_path, language_code = "tr"):
    if os.path.exists(audio_file_path):
        result = model.transcribe(audio_file_path, fp16=False, language=language_code)['text']
        return result

# sending the prompt and receiving response from gpt
def generate_response(conversation, prompt):
    messages = conversation
    messages.append({'role': 'user', 'content': prompt})
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo", # the model that will be used for text generation
        max_tokens=2000, # the maximum number of tokens (words or characters) that the generated output should contain
        n=1, # determines how many alternative completions (the text that the model produces) the model should generate
        stop=None, # stop generating text when these words are generated
        temperature=0.5, # controls the randomness text. A higher value makes the output more creative and varied
        messages = messages
    )
    return response['choices'][0]['message']['content']

# converting text to speech with gTTS
def speak_with_gtts(text, lang = "tr"):
    speech = gTTS(text=text, lang=lang, slow=False)
    file_name = f"speech.mp3"
    if os.path.exists(file_name):
        os.remove(file_name)
    speech.save(file_name)
    playsound.playsound(file_name)
    os.remove(file_name)

# converting text to speech with pyttsx3
def speak_with_pytts(text):
    engine.say(text)
    engine.runAndWait()

st.set_page_config(
    page_title="Voice Assistant Web App",
    layout="wide",
)

# Custom CSS for styling
st.markdown(
    """
    <style>
    .stApp {
        max-width: 800px;
        margin: 0 auto;
        padding: 20px;
    }
    .st-ayw > div > div:first-child {
        padding-top: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True
)

def main():
    st.title("AI Based Voice Assistant")
    st.write("Speak something to the assistant!")

    conversation = []
    recognizer = sr.Recognizer()

    c = 0
    while True:
        with sr.Microphone() as source:
            recognizer.adjust_for_ambient_noise(source, duration=0.2)
            if c == 0:
                st.write("Listening...")
                speak_with_pytts("Dinliyorum")
                c += 1
            source.pause_threshold = 1
            audio = recognizer.listen(source, phrase_time_limit=None, timeout=None)
            transcription = ""
            try:
                transcription = recognizer.recognize_google(audio, language="tr-TR")
            except sr.UnknownValueError:
                st.write("Could not recognize")
            except sr.RequestError:
                st.write("Could not request results; check your network connection")
            if transcription is not None and transcription != "":
                st.write(f"You: {transcription}")
                response = generate_response(conversation, transcription)
                conversation.append({"role": "user", "content": transcription})
                conversation.append({"role": "assistant", "content": response})
                speak_with_pytts(response)
                st.write(f"Assistant: {response}")

if __name__ == "__main__":
    main()









