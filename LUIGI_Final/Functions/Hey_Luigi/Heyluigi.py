import os
import subprocess
import tempfile
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
from gtts import gTTS
import pygame
import google.generativeai as genai
import RPi.GPIO as GPIO
import time

# Configure your Gemini API key (replace with your actual key)
api_key = "AIzaSyBiy1LbIazAYhR34_TxpaDEx53eWe0wi6Q" 
genai.configure(api_key=api_key)

# Initialize pygame mixer
pygame.mixer.init()
DOUBLE_TAP_INTERVAL = 0.5  # Define the double tap interval
# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(5, GPIO.IN, pull_up_down=GPIO.PUD_UP)

double_tap_detected = False

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
        "Error-Code": "Sorry, I couldn't understand that. Please try again.",
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
    response = chat_session.send_message(input_text)
    generated_text = response.text
    return generated_text

def text_to_speech(text, engine='pygame'):
    try:
        if engine == 'pygame':
            tts = gTTS(text=text, lang='en')
            tts.save("output.mp3")
            pygame.mixer.music.load("output.mp3")
            pygame.mixer.music.play()

            # Wait for the speech to finish
            while pygame.mixer.music.get_busy():
                pygame.time.Clock().tick(10)
            os.remove("output.mp3")

        elif engine == 'espeak-ng':
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_file_path = temp_file.name
            temp_file.close()
            subprocess.Popen(['espeak-ng', '-w', temp_file_path, text])
            subprocess.Popen(['aplay', temp_file_path])  # Play asynchronously
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
        # Fallback to gTTS if all other engines fail
        tts = gTTS(text=text, lang='en')
        tts.save("output.mp3")
        subprocess.Popen(['aplay', 'output.mp3'])

def check_double_tap():
    global double_tap_detected
    global last_tap_time, tap_count
    tap_count = 0
    last_tap_time = 0
    start_time = time.time()

    while time.time() - start_time < 0.5:  # 1 second window for double tap
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

def main():
    # Greet the user initially
    greeting_message = "Hello! I am your Luigi. How can I help you today?"
    text_to_speech(greeting_message)

    try:
        while True:
            # Check for double-tap
            check_double_tap()
            if double_tap_detected:
                print("Double tap detected. Exiting...")
                subprocess.run(['python3', '/home/pi/Desktop/LUIGI_Final/Function.py'])
                os._exit(0)  # Terminate the script
                break

            # Record speech for 3 seconds
            record_duration = 3
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

            # Speak the reply
            text_to_speech(reply)

            # Check for exit command
            if input_text.lower() in ["exit", "quit", "bye"]:
                print("Exiting...")
                subprocess.run(['python3', '/home/pi/Desktop/LUIGI_Final/Function.py'])
                os._exit(0)  # Terminate the script
                break

    except KeyboardInterrupt:
        print("Exiting...")

    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    main()
