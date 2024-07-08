import time
import os
import speech_recognition as sr
from pathlib import Path
import openai
import pygame
import pyttsx3
from gtts import gTTS

# Set up OpenAI API key
openai.api_key = "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"

recognizer = sr.Recognizer()
microphone = sr.Microphone()

# Preload TTS engine
engine = pyttsx3.init()
engine.setProperty('rate', 150)
engine.setProperty('volume', 1)
voices = engine.getProperty('voices')
engine.setProperty('voice', voices[1].id)

# Initialize Pygame mixer
pygame.mixer.init()

# Dictionary mapping input strings to reply strings
REPLY_DICT = {
    "hello": "Hi there!",
    "how are you?": "I'm fine, thank you!",
    "bye": "Goodbye!",
    "thank you": "You're welcome!",
    "good morning": "Good morning!",
    "good afternoon": "Good afternoon!",
    "good evening": "Good evening!",
    "how's it going?": "It's going well, thank you!",
    "what's up?": "Not much, just here to assist you!",
    "nice to meet you": "Nice to meet you too!",
    "tell me a joke": "Why don't scientists trust atoms? Because they make up everything!",
    "do you like music?": "I don't have personal preferences, but I can appreciate music!",
    "what's your favorite book?": "I don't have a favorite book, but I enjoy reading about various topics!",
    "where are you from?": "I'm from the digital realm, here to help you!",
    "what do you do for fun?": "I enjoy processing information and assisting users like you!",
}

def speech_to_text():
    with microphone as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        audio = recognizer.listen(source, phrase_time_limit=10)
    try:
        print("Recognizing...")
        return recognizer.recognize_google(audio)
    except (sr.RequestError, sr.UnknownValueError):
        return "Unable to recognize speech"

def get_reply(input_string):
    return REPLY_DICT.get(input_string, generate_text(input_string))

def generate_text(prompt):
    response = openai.ChatCompletion.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful voice assistant."},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message['content']

def speak(text):
    speech_file_path = Path(__file__).parent / "speech.mp3"
    try:
        response = openai.Audio.create(
            model="tts-1",
            voice="alloy",
            input=text
        )
        with open(speech_file_path, "wb") as f:
            f.write(response["audio_content"])

        play_audio(speech_file_path)
    except Exception:
        fallback_tts(text)

def play_audio(file_path):
    pygame.mixer.music.load(file_path)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

def fallback_tts(text):
    try:
        engine.say(text)
        engine.runAndWait()
    except Exception:
        try:
            tts = gTTS(text=text, lang='en')
            output_file = Path(__file__).parent / "output_generate.mp3"
            tts.save(output_file)
            play_audio(output_file)
        except Exception as e:
            print(f"gTTS Error: {e}")

def main():
    while True:
        input_text = speech_to_text()
        print("Input Text: ", input_text)

        reply = get_reply(input_text)
        print("Generated Text: ", reply)

        speak(reply)

        if input_text.lower() == "bye":
            break

        time.sleep(1)

if __name__ == "__main__":
    main()
