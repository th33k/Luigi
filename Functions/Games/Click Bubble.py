import pygame
import random
import time
import subprocess
import os
import threading
import RPi.GPIO as GPIO

# Initialize Pygame
pygame.init()

# Screen settings
screen_width, screen_height = 1024, 768
screen = pygame.display.set_mode((screen_width, screen_height))
pygame.display.set_caption("Whack-a-Mole")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
red = (255, 0, 0)

# Mole settings
mole_radius = 40
mole_safe_zone = 50  # Safe zone for score and timer display

# Game variables
score = 0
font = pygame.font.Font(None, 40)
mole_time_limit = 2  # seconds to click the mole

# GPIO Setup for double-tap detection
TOUCH_PIN = 5
GPIO.setmode(GPIO.BCM)
GPIO.setup(TOUCH_PIN, GPIO.IN)

# Function to draw a mole at a random position
def draw_mole():
    while True:
        pos = (random.randint(mole_radius, screen_width - 2*mole_radius),
               random.randint(mole_radius + mole_safe_zone, screen_height - 2* mole_radius))
        if pos[1] > mole_safe_zone + mole_radius:
            return pos

# Function to display a message on screen
def display_message(message):
    screen.fill(white)
    message_text = font.render(message, True, black)
    screen.blit(message_text, (screen_width // 2 - message_text.get_width() // 2,
                               screen_height // 2 - message_text.get_height() // 2))
    pygame.display.flip()
    time.sleep(2)

# Function to start the double tap detection in a separate thread
def start_double_tap_detection():
    try:
        last_tap_time = 0
        tap_count = 0
        DOUBLE_TAP_INTERVAL = 0.5  # Adjust as needed

        def detect_double_tap():
            nonlocal last_tap_time, tap_count
            while True:
                if GPIO.input(TOUCH_PIN) == GPIO.HIGH:
                    current_time = time.time()
                    
                    if (current_time - last_tap_time) < DOUBLE_TAP_INTERVAL:
                        tap_count += 1
                    else:
                        tap_count = 1  # Reset tap count if the interval is too long
                    
                    last_tap_time = current_time
                    
                    if tap_count == 2:
                        subprocess.Popen(['python3', '/home/pi/Desktop/Luigi/Function.py'])
                        print("Double tap detected! Closing game...")
                        pygame.quit()
                        GPIO.cleanup()
                        os._exit(0)

                    # Debounce delay
                    while GPIO.input(TOUCH_PIN) == GPIO.HIGH:
                        time.sleep(0.01)
                
                time.sleep(0.01)  # Polling interval

        # Run the double tap detection function in a separate thread
        detect_thread = threading.Thread(target=detect_double_tap)
        detect_thread.start()

    except KeyboardInterrupt:
        print("Exiting program")
        GPIO.cleanup()

# Run the double tap detection function
if __name__ == "__main__":
    start_double_tap_detection()

    # Main game loop
    while True:
        mole_position = draw_mole()
        start_time = time.time()
        running = True
        
        while running:
            screen.fill(white)

            # Draw mole
            pygame.draw.circle(screen, black, mole_position, mole_radius)

            # Display score
            score_text = font.render(f"Score: {score}", True, black)
            screen.blit(score_text, (10, 10))

            # Display timer
            elapsed_time = time.time() - start_time
            remaining_time = mole_time_limit - elapsed_time
            timer_text = font.render(f"Time: {remaining_time:.1f}", True, red)
            screen.blit(timer_text, (screen_width - 120, 10))

            # Check for time limit
            if elapsed_time > mole_time_limit:
                display_message(f"Time's up! Your score: {score}")
                running = False
                break

            # Check for events (including double-tap)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    GPIO.cleanup()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    distance = ((mouse_pos[0] - mole_position[0]) ** 2 + (mouse_pos[1] - mole_position[1]) ** 2) ** 0.5
                    if distance < mole_radius:
                        score += 1
                        mole_position = draw_mole()
                        start_time = time.time()

            pygame.display.flip()
            time.sleep(0.1)

        # Display retry message
        display_message("Click to retry")
        waiting = True
        
        while waiting:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    GPIO.cleanup()
                    exit()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    waiting = False
                    score = 0  # Reset score for new game
