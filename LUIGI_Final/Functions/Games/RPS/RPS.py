import time
import threading
import subprocess
import os
import RPi.GPIO as GPIO
import random
import cv2
import cvzone
from cvzone.HandTrackingModule import HandDetector
import pygame

# Initialize constants
WIDTH, HEIGHT = 480, 320
MAX_HANDS = 2
ROUND_COUNT = 3
FINGER_IDENTIFIER_THRESHOLD = 10
PROGRESS_BAR_MAX = 80
DOUBLE_TAP_INTERVAL = 0.5  # Define the double tap interval

# GPIO setup
TOUCH_PIN = 5  # GPIO pin 5 for touch sensor
GPIO.setmode(GPIO.BCM)
GPIO.setup(TOUCH_PIN, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)

# Initialize the hand detector
detector = HandDetector(maxHands=MAX_HANDS)

# Initialize game variables and states
cap = cv2.VideoCapture(0)
cap.set(3, WIDTH)
cap.set(4, HEIGHT)

currentState = 'HOME'
currentRound = 0
playerWinnings = 0
pcWinnings = 0
lastGestureIdentifierValue = 0
fingerIdentifierValues = []
gameRandomNumber = 0
gameScoreProgressBarCounter = 0

# Initialize Pygame for sound
pygame.init()
pygame.mixer.init()

# Pre-load the sound files
sounds = {
    'notify': pygame.mixer.Sound('Resources/notify.wav'),
    'game_music': 'Resources/RPS.mp3'
}

def playSound(name):
    if name == 'game_music':
        pygame.mixer.music.load(sounds[name])
        pygame.mixer.music.play()
    else:
        sounds[name].play()

def fingerGestureDetection(fingers):
    gestures = {
        (0, 0, 0, 0, 0): 1,  # Rock
        (1, 1, 1, 1, 1): 2,  # Paper
        (0, 1, 1, 0, 0): 3,  # Scissor
    }
    return gestures.get(tuple(fingers), 0)

def identifyFingerGesture(fingers):
    global lastGestureIdentifierValue, fingerIdentifierValues
    identifiedGesture = fingerGestureDetection(fingers)
    if lastGestureIdentifierValue == identifiedGesture:
        fingerIdentifierValues.append(identifiedGesture)
        if len(fingerIdentifierValues) > FINGER_IDENTIFIER_THRESHOLD:
            fingerIdentifierValues = []
            playSound('notify')
            return identifiedGesture
    else:
        lastGestureIdentifierValue = identifiedGesture
        fingerIdentifierValues = []
    return 0

def game(hands):
    playSound('game_music')
    global gameRandomNumber, currentState, playerWinnings, pcWinnings, currentRound, imgAI, imgScaled
    imgBG = cv2.imread("Resources/game_bg.png")
    imgBG[182:441, 570:830] = imgScaled

    if hands:
        verifyUserInput = identifyFingerGesture(detector.fingersUp(hands[0]))
        if verifyUserInput > 0:
            currentRound += 1
            gameRandomNumber = random.randint(1, 3)
            if (verifyUserInput - gameRandomNumber) % 3 == 1:
                playerWinnings += 1
            elif (verifyUserInput - gameRandomNumber) % 3 == 2:
                pcWinnings += 1
            currentState = 'GAME_SCORES'

        imgAI = cv2.imread(f'Resources/{gameRandomNumber}.png', cv2.IMREAD_UNCHANGED)
        imgBG = cvzone.overlayPNG(imgBG, imgAI, (69, 181))
    else:
        imgAI = cv2.imread(f'Resources/{gameRandomNumber}.png', cv2.IMREAD_UNCHANGED)
        imgBG = cvzone.overlayPNG(imgBG, imgAI, (69, 181))

    cv2.imshow("Game", imgBG)
    if currentState == 'GAME_SCORES':
        cv2.waitKey(1000)

def gameScores():
    global gameScoreProgressBarCounter, currentState, currentRound
    gameScoreProgressBarCounter += 1
    imgBG = cv2.imread("Resources/game_score_bg.png")
    cv2.putText(imgBG, str(currentRound), (495, 60), cv2.FONT_HERSHEY_DUPLEX, 2, (190, 183, 36), 2)
    cv2.putText(imgBG, str(pcWinnings), (90, 400), cv2.FONT_HERSHEY_DUPLEX, 10, (190, 183, 36), 10)
    cv2.putText(imgBG, str(playerWinnings), (600, 400), cv2.FONT_HERSHEY_DUPLEX, 10, (190, 183, 36), 10)
    cv2.putText(imgBG, gameScoreProgressBarCounter * '|', (130, 480), cv2.FONT_HERSHEY_DUPLEX, 1, (190, 183, 36), 2)
    cv2.imshow("Game", imgBG)

    if gameScoreProgressBarCounter >= PROGRESS_BAR_MAX:
        gameScoreProgressBarCounter = 0
        currentState = 'GAME' if ROUND_COUNT > currentRound else 'FINAL_SCORES'

def finalScores():
    global gameScoreProgressBarCounter, currentState, playerWinnings, pcWinnings, currentRound
    gameScoreProgressBarCounter += 1
    defaultBackground = "draw" if playerWinnings == pcWinnings else 'lost' if pcWinnings > playerWinnings else 'won'
    imgBG = cv2.imread(f"Resources/{defaultBackground}.png")
    cv2.imshow("Game", imgBG)

    if gameScoreProgressBarCounter >= PROGRESS_BAR_MAX:
        gameScoreProgressBarCounter = 0
        resetGame()

def resetGame():
    global playerWinnings, pcWinnings, currentRound, currentState
    playerWinnings = 0
    pcWinnings = 0
    currentRound = 0
    currentState = 'HOME'

def detect_double_tap():
    global last_tap_time, tap_count
    last_tap_time = 0
    tap_count = 0
    try:
        while True:
            if GPIO.input(TOUCH_PIN) == GPIO.HIGH:
                current_time = time.time()
                if (current_time - last_tap_time) < DOUBLE_TAP_INTERVAL:
                    tap_count += 1
                else:
                    tap_count = 1  # Reset tap count if the interval is too long
                last_tap_time = current_time

                if tap_count == 2:
                    print("Double tap detected! Stopping current script and running a new one.")
                    tap_count = 0  # Reset tap count after a double tap
                    # Close all windows
                    cv2.destroyAllWindows()
                    pygame.quit()
                    cap.release()
                    # Run another Python script
                    subprocess.run(['python3', '/home/pi/Desktop/LUIGI_Final/FUNTION.py'])
                    os._exit(0)  # Terminate the script

                # Debounce delay
                while GPIO.input(TOUCH_PIN) == GPIO.HIGH:
                    time.sleep(0.01)

            time.sleep(0.01)
    except KeyboardInterrupt:
        print("Exiting program")
    finally:
        GPIO.cleanup()

def main():
    global imgScaled, currentState
    
    detection_thread = threading.Thread(target=detect_double_tap)
    detection_thread.daemon = True
    detection_thread.start()

    while True:
        videoReadingStatus, frame = cap.read()
        if not videoReadingStatus:
            print("Some error occurred with the camera process. Please check and try again.")
            break

        key = cv2.waitKey(1)
        imgScaled = cv2.resize(frame, (0, 0), None, 0.54, 0.54)[:, 43:303]
        hands, frame = detector.findHands(imgScaled)

        if currentState == 'HOME':
            gameScores()
            currentState = 'GAME'
        elif currentState == 'GAME':
            game(hands)
        elif currentState == 'GAME_SCORES':
            gameScores()
        elif currentState == 'FINAL_SCORES':
            finalScores()

        if currentState == 'HOME':
            break

    pygame.quit()

if __name__ == "__main__":
    main()
