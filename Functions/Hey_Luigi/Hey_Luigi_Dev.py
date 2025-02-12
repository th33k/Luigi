import os
import threading
import time
import socket
import subprocess
import google.generativeai as genai
import pygame
import pyttsx3
import requests
import RPi.GPIO as GPIO
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import webview
from gtts import gTTS

# Define the double tap interval
DOUBLE_TAP_INTERVAL = 0.5

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)

double_tap_detected = False

# Configure your Gemini API key (replace with your actual key)
api_key  = "AIzaSyBPhqUtPSDCWs0Mx5Y88RDDkFNnLmMO7HI"
genai.configure(api_key=api_key)

elevenlabs_api_keys = [
    "sk_ba2d9591949c767083135974b12c5950d6b7b9dcf243d902"
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

def speech_to_text(recognizer, microphone, internet):
    """Convert speech to text."""
    def record_speech(duration, sample_rate=16000):
        recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
        sd.wait()
        return recording

    def save_wav(audio_data, filename, sample_rate):
        sf.write(filename, audio_data, sample_rate)

    def local_recode():
        record_duration = 3
        sample_rate = 16000
        audio_data = record_speech(record_duration, sample_rate)
        audiofile = os.path.join(current_directory, "speech_recording.wav")
        save_wav(audio_data, audiofile, sample_rate)
        with sr.AudioFile(audiofile) as source:
            audio = recognizer.record(source)
        try:
            text = recognizer.recognize_google(audio)
        except sr.UnknownValueError:
            text = "Error-Code"
        return text

    if internet:
        with microphone as source:
            recognizer.adjust_for_ambient_noise(source)
            print("Listening...")
            audio = recognizer.listen(source, phrase_time_limit=10)
        try:
            print("Recognizing...")
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
            "max_output_tokens": 50,
            "response_mime_type": "text/plain",
        }
        model = genai.GenerativeModel(
            model_name="gemini-1.0-pro",
            generation_config=generation_config,
        )
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(input_string)
        return response.text

def text_to_speech(text, engine='pygame'):
    """Convert text to speech using selected engine."""
    try:
        if engine == 'pygame':
            tts = gTTS(text=text, lang='en')
            tts.save("output.mp3")
            pygame.mixer.music.load("output.mp3")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            os.remove("output.mp3")
        elif engine == 'espeak-ng':
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_file_path = temp_file.name
            temp_file.close()
            subprocess.Popen(['espeak-ng', '-w', temp_file_path, text])
            subprocess.Popen(['aplay', temp_file_path])
            os.remove(temp_file_path)
        elif engine == 'festival':
            subprocess.Popen(['festival', '--tts'], input=text.encode('utf-8'))
        elif engine == 'gTTS':
            tts = gTTS(text=text, lang='en')
            tts.save("output.mp3")
            subprocess.Popen(['aplay', 'output.mp3'])
        else:
            raise ValueError(f"Unsupported engine '{engine}'")
    except Exception as e:
        print(f"Error: {e}")
        tts = gTTS(text=text, lang='en')
        tts.save("output.mp3")
        subprocess.Popen(['aplay', 'output.mp3'])

def check_double_tap():
    """Detect a double-tap."""
    global double_tap_detected
    tap_count = 0
    last_tap_time = 0
    start_time = time.time()
    while time.time() - start_time < 0.5:  # 0.5 second window for double tap
        if GPIO.input(5) == GPIO.HIGH:
            current_time = time.time()
            if (current_time - last_tap_time) < DOUBLE_TAP_INTERVAL:
                tap_count += 1
            else:
                tap_count = 1  # Reset tap count if the interval is too long
            last_tap_time = current_time
            if tap_count == 2:
                double_tap_detected = True
                break

def open_webview():
    """Open webview for user interaction."""
    try:
        webview.create_window('Hey Luigi', os.path.join(current_directory, 'web.html'), width=480, height=320, fullscreen=False)
    except Exception as e:
        print("Failed to open webview:", e)

def voice_assistant(internet_status):
    """Main voice assistant function."""
    recognizer = sr.Recognizer()
    microphone = sr.Microphone()
    greeting_message = "Hello! I am your Luigi. How can I help you today?"
    print(greeting_message)
    text_to_speech(greeting_message, engine='pygame')
    try:
        for _ in range(10):
            # Check for double-tap
            check_double_tap()
            if double_tap_detected:
                print("Double tap detected. Exiting...")
                subprocess.run(['python3', '/home/pi/Desktop/Luigi/Function.py'])
                os._exit(0)  # Terminate the script
            text = speech_to_text(recognizer, microphone, internet_status)
            print("You said:", text)
            play_audio(os.path.join(current_directory, 'Resources', 'Audio', 'mmm.wav'))
            answer = answer_generate(text, internet_status)
            print("Answer:", answer)
            if answer in [
                "Sorry, I couldn't recognize your speech. Please try again.",
                "Sorry, the speech recognition service is unavailable.",
                "Sorry, I couldn't understand that. Please try again."
            ]:
                play_audio(os.path.join(current_directory, 'Resources', 'Audio', 'tata.wav'))
                print("Exit: Bye Bye")
                subprocess.run(['python3', '/home/pi/Desktop/Luigi/Function.py'])
                os._exit(0)
            play_audio(os.path.join(current_directory, 'Resources', 'Audio', 'aaha.wav'))
            text_to_speech(answer, engine='pygame')
    except KeyboardInterrupt:
        print("Exiting...")
        os._exit(0)
    finally:
        GPIO.cleanup()

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
