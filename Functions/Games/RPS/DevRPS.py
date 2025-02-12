import random
import time
import cv2
import sys
import os
import cvzone
from cvzone.HandTrackingModule import HandDetector

# Initialize the hand detector
detector = HandDetector(maxHands=2)

# Initialize game variables and states
cap = cv2.VideoCapture(0)
cap.set(3, 640)  # Set the width of the video capture
cap.set(4, 480)  # Set the height of the video capture
timer = 0
stateResult = False
startGame = False
score = [0, 0]
imgAI = None
identifying = False
currentState = 'HOME'
roundCount = 3  # Fixed number of rounds
currentRound = 0
playerWinnings = 0
pcWinnings = 0
lastFingerCountValue = 0
fingerCountValueArray = []
lastGestureIdentifierValue = 0
fingerIdentifierValues = []
gameRandomNumber = 0
gameScoreProgressBarCounter = 0

# Function to play a sound when detecting the hand gesture of the user
def playSound():
    filename = 'Resources/notify.wav'
    # Play sound code should be implemented here

# Identifying either rock or paper or scissor
def fingerGestureDetection(fingers):
    gestures = {
        (0, 0, 0, 0, 0): 1,  # Rock
        (1, 1, 1, 1, 1): 2,  # Paper
        (0, 1, 1, 0, 0): 3,  # Scissor
    }
    return gestures.get(tuple(fingers), 0)

# To identify the correct user gesture avoiding accidental gestures
def identifyFingerGesture(fingers):
    global lastGestureIdentifierValue, fingerIdentifierValues
    identifiedGesture = fingerGestureDetection(fingers)

    if lastGestureIdentifierValue == identifiedGesture:
        fingerIdentifierValues.append(identifiedGesture)
        if len(fingerIdentifierValues) > 10:
            fingerIdentifierValues = []
            playSound()
            return identifiedGesture
        else:
            return 0
    else:
        lastGestureIdentifierValue = identifiedGesture
        fingerIdentifierValues = []
        return 0

# Function to play the game with game logics
def game(hands):
    global gameRandomNumber, currentState, playerWinnings, pcWinnings, currentRound
    imgBG = cv2.imread("Resources/game_bg.png")
    imgBG[182:441, 570:830] = imgScaled

    if len(hands) >= 1:
        verifyUserInput = identifyFingerGesture(detector.fingersUp(hands[0]))

        if verifyUserInput > 0:
            currentRound += 1
            gameRandomNumber = random.randint(1, 3)  # Generate a random number for the computer's move
            if (verifyUserInput - gameRandomNumber) % 3 == 1:
                playerWinnings += 1
            elif (verifyUserInput - gameRandomNumber) % 3 == 2:
                pcWinnings += 1
            currentState = 'GAME_SCORES'  # Move to the game scores state

        imgAI = cv2.imread(f'Resources/{gameRandomNumber}.png', cv2.IMREAD_UNCHANGED)  # Load the computer's move image
        imgBG = cvzone.overlayPNG(imgBG, imgAI, (69, 181))  # Overlay the computer's move image on the background image
        cv2.imshow("Game", imgBG)
        if currentState == 'GAME_SCORES':
            cv2.waitKey(1000)
    else:
        imgAI = cv2.imread(f'Resources/{gameRandomNumber}.png', cv2.IMREAD_UNCHANGED)
        imgBG = cvzone.overlayPNG(imgBG, imgAI, (69, 181))
        cv2.imshow("Game", imgBG)

# Function to display game scores round by round
def gameScores():
    global gameScoreProgressBarCounter, currentState, currentRound
    gameScoreProgressBarCounter += 5
    imgBG = cv2.imread("Resources/game_score_bg.png")

    # Display the current round, PC winnings, and player winnings on the image
    cv2.putText(imgBG, str(currentRound), (495, 60), cv2.FONT_HERSHEY_DUPLEX, 2, (190, 183, 36), 2)
    cv2.putText(imgBG, str(pcWinnings), (90, 400), cv2.FONT_HERSHEY_DUPLEX, 10, (190, 183, 36), 10)
    cv2.putText(imgBG, str(playerWinnings), (600, 400), cv2.FONT_HERSHEY_DUPLEX, 10, (190, 183, 36), 10)

    # Display the game score progress bar based on the gameScoreProgressBarCounter
    cv2.putText(imgBG, gameScoreProgressBarCounter * '|', (130, 480), cv2.FONT_HERSHEY_DUPLEX, 1, (190, 183, 36), 2)
    cv2.imshow("Game", imgBG)

    if gameScoreProgressBarCounter > 15:  # If the game score progress bar is complete
        gameScoreProgressBarCounter = 0
        if roundCount > currentRound:  # If there are more rounds to play
            currentState = 'GAME'
        else:
            currentState = 'FINAL_SCORES'  # Move to the final scores state

# Function to display final scores
def finalScores():
    global gameScoreProgressBarCounter, currentState, playerWinnings, pcWinnings, currentRound
    gameScoreProgressBarCounter += 1
    defaultBackground = "draw"  # Default background image used when tied

    if pcWinnings > playerWinnings:  # If PC has more winnings than the player
        defaultBackground = 'lost'
    elif pcWinnings < playerWinnings:  # If player has more winnings than PC
        defaultBackground = 'won'

    imgBG = cv2.imread("Resources/" + defaultBackground + ".png")
    cv2.imshow("Game", imgBG)  # Show the final scores image

    if gameScoreProgressBarCounter > 79:  # If the game score progress bar is complete
        gameScoreProgressBarCounter = 0
        playerWinnings = 0
        pcWinnings = 0
        currentRound = 0
        currentState = 'HOME'  # Move to the home state

# Main function to organize the game logic
def main():
    global imgScaled, currentState

    while True:
        # Video frame reading process.
        videoReadingStatus, frame = cap.read()

        # Video reading thread has been slept in here.
        key = cv2.waitKey(10)

        # Reading status checked in here.
        if videoReadingStatus:
            # Scaling the captured frame.
            imgScaled = cv2.resize(frame, (0, 0), None, 0.54, 0.54)
            imgScaled = imgScaled[:, 43:303]

            # Identifying the hands in the frame.
            hands, frame = detector.findHands(imgScaled)

            # States of the game
            if currentState == 'HOME':
                currentState = 'GAME'  # Start the game directly
            elif currentState == 'GAME':
                game(hands)
            elif currentState == 'GAME_SCORES':
                gameScores()
            elif currentState == 'FINAL_SCORES':
                finalScores()
        else:
            print("Some error occurred with camera process. Please check and try again.")
            break

if __name__ == "__main__":
    main()
