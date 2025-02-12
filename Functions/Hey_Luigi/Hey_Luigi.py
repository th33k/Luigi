import os
import subprocess
import tempfile
import threading
import time
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
from gtts import gTTS
import pygame
import google.generativeai as genai
import webview  # Added import for webview
import RPi.GPIO as GPIO

# Configure your Gemini API key (replace with your actual key)
api_key = "AIzaSyBPhqUtPSDCWs0Mx5Y88RDDkFNnLmMO7HI"
genai.configure(api_key=api_key)

TOUCH_PIN = 5  # GPIO pin connected to the touch sensor
# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TOUCH_PIN, GPIO.IN)

# Time interval for detecting double tap (in seconds)
DOUBLE_TAP_INTERVAL = 0.5

# Variables to keep track of taps and sensor state
last_tap_time = 0
tap_count = 0
sensor_enabled = True

# Event to signal stopping all operations
stop_event = threading.Event()

# Initialize pygame mixer
pygame.mixer.init()

def record_speech(duration, sample_rate=16000):
    print("Recording...")
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    return recording

def save_wav(audio_data, filename, sample_rate):
    sf.write(filename, audio_data, sample_rate)

def speech_to_text(audiofile):
    rec = sr.Recognizer()
    with sr.AudioFile(audiofile) as source:
        audio = rec.record(source)
    try:
        text = rec.recognize_google(audio)
    except sr.UnknownValueError:
        text = "Error-Code"
    return text

def reply_to_string(input_string):
    reply_dict = {
        "Error-Code": "Hey Buddy, Ask Me any thing?",
        "introduce yourself": "I am Luigi, The First Year Hardware Project of I T Group Number Seven.", 
        "hello": "Hi there!",
        "how are you": "I'm fine, thank you!",
        "bye": "Goodbye!",
        "thank you": "You're welcome!",
        "good morning": "Good morning!",
        "good afternoon": "Good afternoon!",
        "good evening": "Good evening!",
        "meet my sir": "Hello mister sudantha, how are you? i am luigi, the first year hardware project of group 7.It is nice to meet you.Give an A pass for all of myfriends",
        "how's it going?": "It's going well, thank you!",
        "what's up?": "Not much, just here to assist you!",
        "nice to meet you": "Nice to meet you too!",
        "tell me a joke": "Why don't scientists trust atoms? Because they make up everything!",
        "do you like music": "I don't have personal preferences, but I can appreciate music!",
        "what's your favorite book?": "I don't have a favorite book, but I enjoy reading about various topics!",
        "where are you from": "I'm from the digital realm, here to help you!",
        "what do you do for fun": "I enjoy processing information and assisting users like you!",
    }
    if input_string in reply_dict:
        return reply_dict[input_string]
    else:
        return generate_text(input_text=input_string)

def generate_text(input_text):
    generation_config = {
        "temperature": 1,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 8192,
        "response_mime_type": "text/plain",
    }
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,
    )
    chat_session = model.start_chat(history=[])
    response = chat_session.send_message(input_text+ " give me short answer")
    generated_text = response.text
    return generated_text

def text_to_speech(text, engine='pygame'):
    try:
        if engine == 'pygame':
            tts = gTTS(text=text, lang='en')
            tts.save("output.mp3")
            pygame.mixer.music.load("output.mp3")
            pygame.mixer.music.play()
            while pygame.mixer.music.get_busy():
                if stop_event.is_set():
                    pygame.mixer.music.stop()
                    break
                pygame.time.Clock().tick(10)
            os.remove("output.mp3")
        elif engine == 'espeak-ng':
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_file_path = temp_file.name
            temp_file.close()
            subprocess.Popen(['espeak-ng', '-w', temp_file_path, text])
            play_process = subprocess.Popen(['aplay', temp_file_path])  # Play asynchronously
            while play_process.poll() is None:
                if stop_event.is_set():
                    play_process.terminate()
                    break
                time.sleep(0.1)
            os.remove(temp_file_path)
        elif engine == 'festival':
            play_process = subprocess.Popen(['festival', '--tts'], input=text.encode('utf-8'))
            while play_process.poll() is None:
                if stop_event.is_set():
                    play_process.terminate()
                    break
                time.sleep(0.1)
        elif engine == 'gTTS':
            tts = gTTS(text=text, lang='en')
            tts.save("output.mp3")
            play_process = subprocess.Popen(['aplay', 'output.mp3'])
            while play_process.poll() is None:
                if stop_event.is_set():
                    play_process.terminate()
                    break
                time.sleep(0.1)
        else:
            raise ValueError(f"Unsupported engine '{engine}'")
    except Exception as e:
        print(f"Error: {e}")
        tts = gTTS(text=text, lang='en')
        tts.save("output.mp3")
        subprocess.Popen(['aplay', 'output.mp3'])

def detect_double_tap():
    global last_tap_time, tap_count
    try:
        while not stop_event.is_set():
            if GPIO.input(TOUCH_PIN) == GPIO.HIGH:
                current_time = time.time()
                if (current_time - last_tap_time) < DOUBLE_TAP_INTERVAL:
                    tap_count += 1
                else:
                    tap_count = 1  # Reset tap count if the interval is too long
                last_tap_time = current_time

                if tap_count == 2:
                    print("Double tap detected! Stopping sensor readings.")
                    tap_count = 0  # Reset tap count after a double tap

                    # Signal all threads to stop
                    stop_event.set()

                    # Stop all audio playback
                    pygame.mixer.music.stop()

                    # Run the new script
                    subprocess.run(['python', '/home/pi/Desktop/Luigi/Function.py'])
                    os._exit(0)  # Terminate the script

                # Debounce delay
                while GPIO.input(TOUCH_PIN) == GPIO.HIGH:
                    time.sleep(0.01)

            time.sleep(0.01)
    except KeyboardInterrupt:
        print("Exiting program")
    finally:
        GPIO.cleanup()

def open_webview():
    """Open webview for user interaction."""
    pass  # Implement your webview code here

def voice_assistant():
    # Greet the user initially
    greeting_message = "Hello! I am your Luigi. Whats up?"
    text_to_speech(greeting_message)

    try:
        while True:
            # Record speech for 4 seconds
            record_duration = 4
            sample_rate = 16000
            audio_data = record_speech(record_duration, sample_rate)
            audiofile = "speech_recording.wav"
            save_wav(audio_data, audiofile, sample_rate)

            # Convert recorded speech to text
            input_text = speech_to_text(audiofile)
            print("Input Text: ", input_text)

            # Generate a reply
            reply = reply_to_string(input_text)
            print("Generated Text: ", reply)

            new_reply = reply.replace('*', '')

            # Speak the reply
            text_to_speech(new_reply)

            # Check for exit command
            if input_text.lower() in ["exit", "quit", "bye"]:
                print("Exiting...")
                break

    except KeyboardInterrupt:
        print("Exiting...")

def main():
    # Start the double tap detection in a separate thread
    detection_thread = threading.Thread(target=detect_double_tap)
    detection_thread.start()

    # Start the voice assistant in a separate thread
    assistant_thread = threading.Thread(target=voice_assistant)
    assistant_thread.start()

    # Run the webview in the main thread
    open_webview()

    # Wait for the threads to finish (although they will run indefinitely until Ctrl+C is pressed)
    detection_thread.join()
    assistant_thread.join()

if __name__ == "__main__":
    main()
