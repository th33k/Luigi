import time
import speech_recognition as sr
from pathlib import Path
import openai
import pygame

# Set up OpenAI API key
openai.api_key = "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"

recognizer = sr.Recognizer()
microphone = sr.Microphone()

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
    if input_string in REPLY_DICT:
        return REPLY_DICT[input_string]
    else:
        response = openai.ChatCompletion.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": "You are a helpful voice assistant."},
                {"role": "user", "content": input_string}
            ]
        )
        return response.choices[0].message['content']

def speak(text):
    speech_file_path = Path(__file__).parent / "speech.mp3"
    response = openai.Audio.create(
        model="tts-1",
        voice="alloy",
        input=text
    )
    with open(speech_file_path, "wb") as f:
        f.write(response["audio_content"])

    pygame.mixer.init()
    pygame.mixer.music.load(speech_file_path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

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
