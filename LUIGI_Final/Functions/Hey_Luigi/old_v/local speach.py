import os
import threading
import time
import socket
import pygame
import requests
import speech_recognition as sr
import sounddevice as sd
import soundfile as sf
import pyttsx3
from gtts import gTTS
import webview
import google.generativeai as genai
from vosk import Model, KaldiRecognizer

# Configuration
gemini_api_key = "AIzaSyBiy1LbIazAYhR34_TxpaDEx53eWe0wi6Q"
genai.configure(api_key=gemini_api_key)

elevenlabs_api_keys = [
    "c506c8567a9fb92d06e59e063d9c0fdc",
    "<api-key-2>",
    "<api-key-3>",
    "<api-key-4>",
    "<api-key-5>"
]
current_directory = os.path.dirname(os.path.realpath(__file__))

# Initialize Pygame for audio playback
pygame.mixer.init()

def check_internet_connection(host="8.8.8.8", port=53, timeout=3):
    """Check for internet connectivity."""
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        print("Internet is available.")
        return True
    except socket.error:
        print("No internet connection.")
        return False

def play_audio(file):
    """Play audio file using Pygame."""
    try:
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
    except pygame.error as e:
        print("Pygame error:", e)

def local_recode():
    """Offline speech recognition using Vosk."""
    model_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "Resources", "vosk-model-small-en-us-0.15")

    if not os.path.exists(model_path):
        print(f"Model not found at {model_path}")
        return "Model not found"

    model = Model(model_path)
    recognizer = KaldiRecognizer(model, 16000)

    with sr.Microphone() as source:
        recognizer.adjust_for_ambient_noise(source)
        print("Listening...")
        audio_data = recognizer.listen(source, phrase_time_limit=10)

    if recognizer.AcceptWaveform(audio_data.get_wav_data()):
        result = recognizer.Result()
        return result.get("text", "Unable to recognize speech")
    else:
        return "Unable to recognize speech"

def speech_to_text(recognizer, microphone, internet):
    """Convert speech to text."""
    if internet:
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            audio = recognizer.listen(source, phrase_time_limit=10)
        try:
            return recognizer.recognize_google(audio)
        except sr.RequestError:
            return "API unavailable"
        except sr.UnknownValueError:
            return "Unable to recognize speech"
    else:
        return local_recode()

def answer_generate(input_string, internet):
    """Generate an answer based on the input string."""
    reply_dict = {
        "Error-Code": "Sorry, I couldn't understand that. Please try again.",
        "API unavailable": "Sorry, the speech recognition service is unavailable.",
        "Unable to recognize speech": "Sorry, I couldn't recognize your speech. Please try again.",
        "hello": "Hi there!",
        "how are you?": "I'm fine, thank you!",
        "bye": "Goodbye!",
        "thank you": "You're welcome!",
        "what's your name?": "I am Luigi, your buddy.",
        "good morning": "Good morning!",
        "good afternoon": "Good afternoon!",
        "good evening": "Good evening!"
    }

    if input_string in reply_dict:
        return reply_dict[input_string]
    elif not internet:
        return "Oh, your internet connection is unstable."
    else:
        generation_config = {
            "temperature": 1,
            "top_p": 0.90,
            "top_k": 64,
            "max_output_tokens": 100,
            "response_mime_type": "text/plain",
        }
        model = genai.GenerativeModel(
            model_name="gemini-1.0-pro",
            generation_config=generation_config,
        )
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(input_string)
        return response.text

def text_to_speech(answer, internet):
    """Convert text to speech using Eleven Labs API or local TTS."""
    def use_elevenlabs(answer):
        CHUNK_SIZE = 1024
        url = "https://api.elevenlabs.io/v1/text-to-speech/Re2sfBwSAP5Hdn5a6Jkt"
        data = {
            "text": answer,
            "model_id": "eleven_monolingual_v1",
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.5,
                "use_speaker_boost": True
            }
        }
        for api_key in elevenlabs_api_keys:
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": api_key
            }
            response = requests.post(url, json=data, headers=headers)
            if response.status_code == 200:
                output_file = os.path.join(current_directory, 'output_generate.mp3')
                with open(output_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                        if chunk:
                            f.write(chunk)
                print("Audio file saved as output_generate.mp3")
                return output_file
            else:
                print(f"Failed with API key: {api_key}. Status code: {response.status_code}")

        return use_local_tts(answer)

    def use_local_tts(answer):
        try:
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)
            engine.setProperty('volume', 1)
            voices = engine.getProperty('voices')
            engine.setProperty('voice', voices[1].id)
            engine.say(answer)
            engine.runAndWait()
        except Exception as e:
            print(f"pyttsx3 Error: {e}")
            try:
                tts = gTTS(text=answer, lang='en')
                output_file = os.path.join(current_directory, 'output_generate.mp3')
                tts.save(output_file)
                return output_file
            except Exception as e:
                print(f"gTTS Error: {e}")
                return None

    if internet:
        output_file = use_elevenlabs(answer)
    else:
        output_file = use_local_tts(answer)

    if output_file:
        play_audio(output_file)
        os.remove(output_file)

def open_webview():
    """Open webview for user interaction."""
    try:
        webview.create_window('Hey Luigi', os.path.join(current_directory, '../web/web.html'), width=480, height=320, fullscreen=False)
    except Exception as e:
        print("Failed to open webview:", e)

def voice_assistant(internet_status):
    """Main voice assistant function."""
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()

    greeting_message = "Hello! I am your Luigi. How can I help you today?"
    print(greeting_message)
    play_audio(os.path.join(current_directory, 'Resources', 'hello_Luigi.mp3'))

    try:
        for _ in range(10):
            text = speech_to_text(recognizer, microphone, internet_status)
            print("You said:", text)
            play_audio(os.path.join(current_directory, 'Resources', 'mmm.wav'))
            answer = answer_generate(text, internet_status)
            print("Answer:", answer)
            if answer in [
                "Sorry, I couldn't recognize your speech. Please try again.",
                "Sorry, the speech recognition service is unavailable.",
                "Sorry, I couldn't understand that. Please try again."
            ]:
                play_audio(os.path.join(current_directory, 'Resources', 'mmm.wav'))
                print("Exit: Bye Bye")
                break
            play_audio(os.path.join(current_directory, 'Resources', 'aaha.wav'))
            text_to_speech(answer, internet_status)
    except KeyboardInterrupt:
        print("Exiting...")

def main():
    """Main function to start the voice assistant and webview."""
    internet_status = check_internet_connection()

    voice_thread = threading.Thread(target=voice_assistant, args=(internet_status,))
    voice_thread.start()

    time.sleep(1)

    open_webview()
    webview.start()

    voice_thread.join()
    print("Voice assistant thread has finished executing.")

if __name__ == "__main__":
    main()
