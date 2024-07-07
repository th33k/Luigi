import speech_recognition as sr
from functions import fun1, fun2, fun3

# Create a dictionary mapping commands to functions
command_to_function = {
    "Rock_Dance": fun1,
    "Ganster Buddy": fun2,
    "Happy Birthday": fun3
}

def recognize_speech_from_mic(recognizer, mic):
    with mic as source:
        print("Listening...")
        recognizer.adjust_for_ambient_noise(source, duration=0.5)
        audio = recognizer.listen(source, timeout=3, phrase_time_limit=3)

    try:
        transcription = recognizer.recognize_google(audio).lower()
        return transcription
    except sr.RequestError:
        # API was unreachable or unresponsive
        return "API unavailable"
    except sr.UnknownValueError:
        # speech was unintelligible
        return "Unable to recognize speech"

# Main program
if __name__ == "__main__":
    recognizer = sr.Recognizer()
    mic = sr.Microphone()

    while True:
        print("Please say a command:")
        spoken_text = recognize_speech_from_mic(recognizer, mic)
        print(f"You said: {spoken_text}")

        # Check if the spoken text matches any command
        if spoken_text in command_to_function:
            # Stop listening for new commands while executing the function
            command_to_function[spoken_text]()  # Call the corresponding function
        else:
            print("Command not recognized.")
