import os
import pygame
import socket
import requests
import speech_recognition as sr
import sounddevice as sd
import soundfile as sf
import google.generativeai as genai
import pyttsx3
from gtts import gTTS

# Configure Gemini API key
gemini_api_key = "AIzaSyBiy1LbIazAYhR34_TxpaDEx53eWe0wi6Q" 
genai.configure(api_key=gemini_api_key)

elevenlabs_api_keys = [
    "sk_1fbcccdd635adc3cf90b823c8151388899642e0fccec35bd",
    "<api-key-2>",
    "<api-key-3>",
    "<api-key-4>",
    "<api-key-5>"
]

current_directory = os.path.dirname(os.path.realpath(__file__))

def check_internet_connection(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        print("Internet is available.")
        return True
    except socket.error:
        print("No internet connection.")
        return False

def record_speech(duration, sample_rate=16000):
    print("Recording...")
    recording = sd.rec(int(duration * sample_rate), samplerate=sample_rate, channels=1, dtype='float32')
    sd.wait()
    return recording

def save_wav(audio_data, filename, sample_rate):
    sf.write(filename, audio_data, sample_rate)

def speech_to_text():
    print("Converting speech to text...")
    if Internet:
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()
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
        audiofile = os.path.join(current_directory, "speech_recording.wav")
        record_duration = 3
        sample_rate = 16000
        audio_data = record_speech(record_duration, sample_rate)
        save_wav(audio_data, audiofile, sample_rate)
        rec = sr.Recognizer()
        with sr.AudioFile(audiofile) as source:
            audio = rec.record(source)
        try:
            text = rec.recognize_google(audio)
        except sr.UnknownValueError:
            text = "Error-Code"
        return text

def answer_generate(input_string):
    print("Generating answer...")
    reply_dict = {
        "Error-Code": "Sorry, I couldn't understand that. Please try again.",
        "hello": "Hi there!",
        "how are you?": "I'm fine, thank you!",
        "bye": "Goodbye!",
        "thank you": "You're welcome!",
        "good morning": "Good morning!",
        "good afternoon": "Good afternoon!",
        "good evening": "Good evening!"
    }

    if input_string in reply_dict:
        return reply_dict[input_string]
    else:
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 100,
            "response_mime_type": "text/plain",
        }
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
        )
        chat_session = model.start_chat(history=[])
        response = chat_session.send_message(input_string)
        generated_text = response.text
        return generated_text

def play_audio(file):
    pygame.init()
    pygame.mixer.init()
    try:
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)
        pygame.mixer.music.stop()
    except pygame.error as e:
        print("Pygame error:", e)
    finally:
        pygame.quit()

def text_to_speech(answer):
    print("Converting text to speech...")
    if Internet:
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
                output_file = os.path.join(current_directory, 'output.mp3')
                with open(output_file, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                        if chunk:
                            f.write(chunk)
                print("Audio file saved as output.mp3")
                play_audio(output_file)
                return
            else:
                print(f"Failed with API key: {api_key}. Status code: {response.status_code}")
                text_to_speech_offline(answer)
    else:
        def text_to_speech_offline():
            try:
                engine = pyttsx3.init()
                engine.setProperty('rate', 150)
                engine.setProperty('volume', 1)
                voices = engine.getProperty('voices')
                engine.setProperty('voice', voices[0].id)
                engine.say(answer)
                engine.runAndWait()
            except Exception as e:
                print(f"pyttsx3 Error: {e}")
                try:
                    tts = gTTS(text=answer, lang='en')
                    output_file = os.path.join(current_directory, 'output.mp3')
                    tts.save(output_file)
                    play_audio(output_file)
                    os.remove(output_file)
                except Exception as e:
                    print(f"gTTS Error: {e}")

def main():
    greeting_message = "Hello! I am your Luigi. How can I help you today?"
    print(greeting_message)

    global Internet
    Internet = check_internet_connection()

    try:
        n = 0
        while n < 1:
            text = speech_to_text()
            answer = answer_generate(text)
            print("Answer:", answer)
            text_to_speech(answer)
            n += 1
    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    main()
