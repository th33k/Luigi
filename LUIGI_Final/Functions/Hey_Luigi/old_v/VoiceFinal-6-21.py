import os
import time
import sounddevice as sd
import soundfile as sf
import speech_recognition as sr
import google.generativeai as genai
import pyttsx3
from gtts import gTTS
import subprocess
import tempfile

# Configure your Gemini API key (replace with your actual key)
api_key = "AIzaSyBiy1LbIazAYhR34_TxpaDEx53eWe0wi6Q" 
genai.configure(api_key=api_key)

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
    # Dictionary mapping input strings to reply strings (optional)
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

    # Check if input_string exists in the dictionary (optional)
    if input_string in reply_dict:
        return reply_dict[input_string]
    else:
        return generate_text(input_text=input_string)

def generate_text(input_text):
    # Create the model
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

    # Start a chat session
    chat_session = model.start_chat(history=[])

    # Send the message to the chat session
    response = chat_session.send_message(input_text)

    # Extract and return the chatbot's response
    generated_text = response.text
    return generated_text

def text_to_speech(text, engine='pyttsx3'):
    try:
        if engine == 'pyttsx3':
            engine = pyttsx3.init()
            engine.setProperty('rate', 150)  # Speed of speech
            engine.setProperty('volume', 1)  # Volume (0.0 to 1.0)
        
            voices = engine.getProperty('voices')
            engine.setProperty('voice', voices[0].id)  # Select the first available male voice
        
            engine.say(text)
            engine.runAndWait()
        
        elif engine == 'espeak-ng':
            temp_file = tempfile.NamedTemporaryFile(suffix='.wav', delete=False)
            temp_file_path = temp_file.name
            temp_file.close()
            
            subprocess.run(['espeak-ng', '-w', temp_file_path, text])
            subprocess.run(['aplay', temp_file_path])  # Replace with your system's audio player command
            
            os.remove(temp_file_path)
        
        elif engine == 'festival':
            subprocess.run(['festival', '--tts'], input=text.encode('utf-8'))
        
        elif engine == 'marytts':
            mary_cmd = f'echo "{text}" | marytts-client'
            subprocess.run(mary_cmd, shell=True)
        
        elif engine == 'picotts':
            subprocess.run(['pico2wave', '-w', 'output.wav', '-l', 'en-US', text])
            subprocess.run(['aplay', 'output.wav'])  # Replace with your system's audio player command
            os.remove('output.wav')
        
        elif engine == 'mozilla-tts':
            mozilla_cmd = f'mozilla-tts --text "{text}" --out_path output.wav'
            subprocess.run(mozilla_cmd, shell=True)
            subprocess.run(['aplay', 'output.wav'])  # Replace with your system's audio player command
            os.remove('output.wav')
        
        else:
            raise ValueError(f"Unsupported engine '{engine}'")
    
    except Exception as e:
        print(f"Error: {e}")
        # Fallback to gTTS if all other engines fail
        tts = gTTS(text=text, lang='en')
        tts.save("output.mp3")
        os.system("start output.mp3")  # Play the generated audio file
def main():
    # Greet the user initially
    greeting_message = "Hello! I am your Luigi. How can I help you today?"
    text_to_speech(greeting_message)

    try:
        while True:
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
                break

    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    main()