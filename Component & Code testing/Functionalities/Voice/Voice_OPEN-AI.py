import time                         # Helps with time-related stuff (waiting or tracking time)
import sounddevice as sd            # Lets us record and play sounds
import soundfile as sf              # Helps read and write sound files.
import speech_recognition as sr     # Understands spoken words and changes them to text.
from pathlib import Path
from openai import OpenAI

# Set up OpenAI API key
openai = OpenAI(api_key="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")

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
        text = "bye"

    return text

def reply_to_string(input_string):
    # Dictionary mapping input strings to reply strings
    reply_dict = {
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
        # Add more mappings as needed
    }

    # Check if input_string exists in the dictionary
    if input_string in reply_dict:
        return reply_dict[input_string]
    else:
        return generate_text(input_string)
    

def generate_text(prompt):
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful voice assistant."},
            {"role": "user", "content": prompt}
        ]
    )

    # Extract the generated text from the response
    generated_text = response.choices[0].message.content
    generated_text_X = " " + generated_text
    return generated_text_X

def speak(text):
    speech_file_path = Path(__file__).parent / "speech.mp3"
    response = openai.audio.speech.create(
        model="tts-1",
        voice="alloy",
        input=text
        # (alloy, echo, fable, onyx, nova, and shimmer)
    )
    response.stream_to_file(speech_file_path)

    # Play the generated speech
    import pygame
    pygame.mixer.init()
    pygame.mixer.music.load(speech_file_path)
    pygame.mixer.music.play()

    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

# Run the script constantly until you close it
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

    # Synthesize the generated text using gTTS
    speak(reply)

    if input_text.lower() == "bye":  # Check for "bye" correctly
        break  # Exit the loop

    # Add a delay of 1 second before recording speech again
    time.sleep(1)
