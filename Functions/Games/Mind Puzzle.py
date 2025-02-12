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
pygame.display.set_caption("Memory Game")

# Colors
white = (255, 255, 255)
black = (0, 0, 0)
colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0), (0, 255, 255), (255, 0, 255), (128, 0, 128), (255, 165, 0)]

# Card settings
card_width, card_height = 230, 205
card_margin = 20

# Generate card positions and values
cards = [(i // 2) for i in range(12)]
random.shuffle(cards)
cards = [cards[i * 4:(i + 1) * 4] for i in range(3)]
card_rects = [[pygame.Rect(x * (card_width + card_margin) + card_margin, y * (card_height + card_margin) + card_margin, card_width, card_height) for x in range(4)] for y in range(3)]
revealed = [[False] * 4 for _ in range(3)]
selected = []
matches = 0

# Game variables
font = pygame.font.Font(None, 50)

# GPIO Setup for double-tap detection
TOUCH_PIN = 5
GPIO.setmode(GPIO.BCM)
GPIO.setup(TOUCH_PIN, GPIO.IN)

def draw_board():
    screen.fill(white)
    for y in range(3):
        for x in range(4):
            if revealed[y][x]:
                pygame.draw.rect(screen, colors[cards[y][x]], card_rects[y][x])
            else:
                pygame.draw.rect(screen, black, card_rects[y][x])
    pygame.display.flip()

def show_message(message):
    text = font.render(message, True, black)
    screen.blit(text, (screen_width // 2 - text.get_width() // 2, screen_height // 2 - text.get_height() // 2))
    pygame.display.flip()

def check_match():
    global selected, matches
    x1, y1 = selected[0]
    x2, y2 = selected[1]
    if cards[y1][x1] == cards[y2][x2]:
        revealed[y1][x1] = True
        revealed[y2][x2] = True
        matches += 1
    else:
        draw_board()
        time.sleep(0.5)
        revealed[y1][x1] = False
        revealed[y2][x2] = False
        draw_board()
    selected = []

def check_win():
    return matches == 6  # 6 matches means all pairs are found

def draw_retry_button():
    retry_text = font.render("Retry", True, black)
    retry_rect = pygame.Rect(screen_width // 2 - 50, screen_height // 2 + 20, 100, 50)
    pygame.draw.rect(screen, white, retry_rect)
    pygame.draw.rect(screen, black, retry_rect, 2)
    screen.blit(retry_text, (screen_width // 2 - retry_text.get_width() // 2, screen_height // 2 + 30))
    pygame.display.flip()
    return retry_rect

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

if __name__ == "__main__":
    start_double_tap_detection()

    # Main game loop
    running = True
    while running:
        draw_board()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                for y in range(3):
                    for x in range(4):
                        if card_rects[y][x].collidepoint(mouse_pos) and not revealed[y][x] and (x, y) not in selected:
                            if len(selected) < 2:
                                selected.append((x, y))
                                revealed[y][x] = True
                                draw_board()
                                if len(selected) == 2:
                                    check_match()
                                    if check_win():
                                        show_message("You've completed the game.")
                                        retry_rect = draw_retry_button()
                                        waiting = True
                                        while waiting:
                                            for event in pygame.event.get():
                                                if event.type == pygame.QUIT:
                                                    running = False
                                                    waiting = False
                                                elif event.type == pygame.MOUSEBUTTONDOWN:
                                                    if retry_rect.collidepoint(event.pos):
                                                        # Reset game
                                                        cards = [(i // 2) for i in range(12)]
                                                        random.shuffle(cards)
                                                        cards = [cards[i * 4:(i + 1) * 4] for i in range(3)]
                                                        revealed = [[False] * 4 for _ in range(3)]
                                                        selected = []
                                                        matches = 0
                                                        draw_board()
                                                        waiting = False
                                        draw_board()

    pygame.quit()
    GPIO.cleanup()
