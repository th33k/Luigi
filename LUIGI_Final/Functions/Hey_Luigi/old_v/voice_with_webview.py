import os
import time
import threading
import pygame
import socket
import requests
import webview
import speech_recognition as sr
import google.generativeai as genai

# Configure Gemini API key
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

# Global variable to track internet connection
Internet = False

def check_internet_connection(host="8.8.8.8", port=53, timeout=3):
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        print("Internet is available.")
        return True
    except socket.error:
        print("No internet connection.")
        return False

def speech_to_text():
    # Placeholder for speech-to-text functionality
    print("Converting speech to text...")

    if Internet:
        recognizer = sr.Recognizer()
        microphone = sr.Microphone()

        def recognize_speech_from_mic(recognizer, microphone, phrase_time_limit=10):
            """Transcribe speech from recorded from `microphone`."""
            with microphone as source:
                recognizer.adjust_for_ambient_noise(source)
                print("Listening...")
                audio = recognizer.listen(source, phrase_time_limit=phrase_time_limit)
        
            try:
                print("Recognizing...")
                return recognizer.recognize_google(audio)
            except sr.RequestError:
                return "API unavailable"
            except sr.UnknownValueError:
                return "Unable to recognize speech"

        text = recognize_speech_from_mic(recognizer, microphone, phrase_time_limit=10)
        print("You said:", text)
        return text
    else:
        print("No internet connection. Cannot convert speech to text.")

def answer_generate(input_string):
    # Placeholder for answer generation functionality
    print("Generating answer...")
    # Dictionary mapping input strings to reply strings (optional)
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

    # Check if input_string exists in the dictionary
    if (input_string := input_string.lower()) in reply_dict:
        return reply_dict[input_string]
    else:
        # Create the model for generative responses
        generation_config = {
            "temperature": 1,
            "top_p": 0.95,
            "top_k": 64,
            "max_output_tokens": 50,
            "response_mime_type": "text/plain",
        }

        # Instantiate the generative model (replace with actual implementation)
        model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config=generation_config,
        )

        # Start a chat session
        chat_session = model.start_chat(history=[])

        # Send the message to the chat session
        response = chat_session.send_message(input_string)

        # Extract and return the chatbot's response
        generated_text = response.text
        return generated_text

def text_to_speech(answer):
    # Placeholder for text-to-speech functionality
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
                # Play the generated audio file
                play_audio(output_file)
                return
            else:
                print(f"Failed with API key: {api_key}. Status code: {response.status_code}")

    else:
        print("No internet connection. Cannot convert text to speech.")

def play_audio(file):
    pygame.init()
    pygame.mixer.init()

    try:
        pygame.mixer.music.load(file)
        pygame.mixer.music.play()

        # Wait for the music to finish playing
        while pygame.mixer.music.get_busy():
            pygame.time.Clock().tick(10)

        pygame.mixer.music.stop()

    except pygame.error as e:
        print("Pygame error:", e)
    finally:
        pygame.quit()

def open_webview():
    # Function to open the webview window
    try:
        webview.create_window('Hey Luigi', os.path.join(current_directory, '../web/web.html'), width=480, height=320, fullscreen=False)
    except Exception as e:
        print("Failed to open webview:", e)

def Voice():

    global Internet
    Internet = check_internet_connection()

    greeting_message = "Hello! I am your Luigi. How can I help you today?"
    print(greeting_message)
    play_audio(os.path.join(current_directory, 'hello_Luigi.mp3')) # Play the greeting message

    try:
        n = 0
        while n < 10:
            text = speech_to_text()

            answer = answer_generate(text)
            print("Answer:", answer)

            text_to_speech(answer)
            n += 1
    except KeyboardInterrupt:
        print("Exiting...")

def main():
    try:
        # Create a thread for the voice assistant
        voice_thread = threading.Thread(target=Voice)
        voice_thread.start()

        # Wait briefly to ensure Internet status is checked
        time.sleep(1)

        # Open webview on the main thread
        open_webview()
        webview.start()

        # Join the voice assistant thread
        voice_thread.join()

        print("Voice assistant thread has finished executing.")
        
    except KeyboardInterrupt:
        print("Exiting...")

if __name__ == "__main__":
    main()
