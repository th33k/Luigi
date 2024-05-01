import pygame
import os

# Initialize pygame
pygame.init()

def play_audio(num):
    try:
        # Get the path to the audio file
        audio_file = os.path.join(os.path.dirname(__file__), "Audio", f"{num}.mp3")     #inside Audio Folder
        
        # Check if the audio file exists
        if not os.path.exists(audio_file):
            raise FileNotFoundError("Audio file not found.")
        
        # Load and play the audio file
        pygame.mixer.music.load(audio_file)
        pygame.mixer.music.play()
        while pygame.mixer.music.get_busy():
            continue
    except (pygame.error, FileNotFoundError) as e:
        print(f"Error: {e}")

def main():
    try:
        while True:
            user_input = input("Enter a number (1-5) or 'q' to quit: ")
            if user_input.lower() == 'q':
                break
            num = int(user_input)
            if 1 <= num <= 5:
                play_audio(num)
            else:
                print("Invalid input. Please enter a number between 1 and 5.")
    except ValueError:
        print("Invalid input. Please enter a valid number or 'q' to quit.")

if __name__ == "__main__":
    main()
