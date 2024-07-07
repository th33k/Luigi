import random
import time
import cv2
import sys, os
import cvzone
from cvzone.HandTrackingModule import HandDetector

# import simpleaudio as sa

detector = HandDetector(maxHands=2)
cap = cv2.VideoCapture(0)

# Initialize game variables and states
cap.set(3, 640)
cap.set(4, 480)
timer = 0
stateResult = False
startGame = False
score = [0, 0]
imgAI = None
identifying = False
currentState = 'HOME'
roundCount = 0
currentRound = 0
totalOngoingRounds = 0
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
    # wave_obj = sa.WaveObject.from_wave_file(filename)
    # play_obj = wave_obj.play()
    # play_obj.wait_done()  # Wait until sound has finished playing


# Identifying either rock or paper or scissor
def fingerGestureDetection(fingers):
    gestures = {
        (0, 0, 0, 0, 0): 1,  # Rock
        (1, 1, 1, 1, 1): 2,  # paper
        (0, 1, 1, 0, 0): 3,  # Scissor
    }
    return gestures.get(tuple(fingers), 0)


# To identify the correct user gesture avoiding accidental gestures
def identifyFingerGesture(fingers):
    global lastGestureIdentifierValue, fingerIdentifierValues
    identifiedGesture = fingerGestureDetection(fingers)

    if (lastGestureIdentifierValue == identifiedGesture):
        fingerIdentifierValues.append(identifiedGesture)
        # taking the gesture which has been detected for more than 10 consecutive frames.
        if (len(fingerIdentifierValues) > 10):
            fingerIdentifierValues = []
            playSound()
            return identifiedGesture
        else:
            return 0
    else:
        lastGestureIdentifierValue = identifiedGesture
        fingerIdentifierValues = []
        return 0


# using when taking the round count from the user
def calculateFingerCount(hands):
    if len(hands) == 1:  # if there is one hand in the frame
        return sum(detector.fingersUp(hands[0]))
    else:
        # if there are two hands in the frame
        return sum(detector.fingersUp(hands[0])) + sum(detector.fingersUp(hands[1]))


def getFingerCount(hands):
    global fingerCountValueArray, lastFingerCountValue
    fingerCount = calculateFingerCount(hands)  # Calculate the finger count using the calculateFingerCount function

    if (lastFingerCountValue == fingerCount):
        fingerCountValueArray.append(fingerCount)
        if (len(fingerCountValueArray) > 10):
            fingerCountValueArray = []
            playSound()
            return fingerCount  # Return the finger count
        else:
            return 0
    else:
        lastFingerCountValue = fingerCount
        fingerCountValueArray = []  # Reset the value array
        return 0


# home page of the game
def handleHome(hands):
    global currentState
    imgBG = cv2.imread("Resources/home_page_bg.png")
    imgBG[122:381, 520:780] = imgScaled

    # making the window full screen
    # cv2.namedWindow("Game", cv2.WINDOW_NORMAL)
    # cv2.setWindowProperty("Game", cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)

    # showing the game Window
    cv2.imshow("Game", imgBG)

    if len(hands) >= 1:
        # getting the hand users current hand gesture
        selectedValueForHomePage = identifyFingerGesture(detector.fingersUp(hands[0]))
        # If users gesture equals to rock
        if (selectedValueForHomePage == 1):
            currentState = 'ROUNDS_COUNT'
        # if the users gesture is equal to paper exiting
        elif (selectedValueForHomePage == 2):
            print("Bye Bye. Have a nice day")
            sys.exit(0)


# Function to handle the rounds count selection
def roundsCount(hands):
    global roundCount, currentState
    imgBG = cv2.imread("Resources/round_count_bg.png")
    imgBG[205:464, 322:582] = imgScaled
    cv2.imshow("Game", imgBG)

    if len(hands) >= 1:
        fingerCount = getFingerCount(hands)  # Get the finger count using the getFingerCount function
        if (fingerCount > 0):
            roundCount = fingerCount
            currentState = 'VERIFY_ROUNDS'  # Move to the verification state to confirm the selected round count


# Function to verify the selected round count
def verifyRounds(hands):
    global currentState, roundCount
    imgBG = cv2.imread("Resources/round_verify_bg.png")
    imgBG[122:381, 540:800] = imgScaled
    cv2.putText(imgBG, str("Is it " + str(roundCount) + " ?"), (350, 70), cv2.FONT_HERSHEY_TRIPLEX, 2, (190, 183, 36),
                4)
    cv2.imshow("Game", imgBG)

    if len(hands) >= 1:
        verifyUserInput = identifyFingerGesture(detector.fingersUp(hands[0]))  # Get the user's finger gesture
        if (verifyUserInput == 1):
            time.sleep(2)  # Wait for 2 seconds
            currentState = 'GAME'  # Move to the game state
        elif (verifyUserInput == 2):
            currentState = 'ROUNDS_COUNT'  # Move back to the rounds count selection state


# Function to play the game with game logics
def game(hands):
    global gameRandomNumber, currentState, playerWinnings, pcWinnings, totalOngoingRounds, currentRound
    imgBG = cv2.imread("Resources/game_bg.png")
    imgBG[182:441, 570:830] = imgScaled

    if len(hands) >= 1:
        verifyUserInput = identifyFingerGesture(detector.fingersUp(hands[0]))
        totalOngoingRounds += 1  # Increment the total ongoing rounds count

        if verifyUserInput > 0:
            currentRound += 1
            gameRandomNumber = random.randint(1, 3)     # Generate a random number for the computer's move
            if (verifyUserInput - gameRandomNumber) % 3 == 1:
                playerWinnings += 1
            elif (verifyUserInput - gameRandomNumber) % 3 == 2:
                pcWinnings += 1
            currentState = 'GAME_SCORES'    # Move to the game scores state
            # player wins
            # if (playerMove == 1 and randomNumber == 3) or \
            #         (playerMove == 2 and randomNumber == 1) or \
            #         (playerMove == 3 and randomNumber == 2):
            #     playerWinnings += 1

            # PC wins
            # if (playerMove == 1 and randomNumber == 2) or \
            #         (playerMove == 2 and randomNumber == 3) or \
            #         (playerMove == 3 and randomNumber == 1):
            #     pcWinnings += 1
        imgAI = cv2.imread(f'Resources/{gameRandomNumber}.png', cv2.IMREAD_UNCHANGED)   # Load the computer's move image
        imgBG = cvzone.overlayPNG(imgBG, imgAI, (69, 181))  # Overlay the computer's move image on the background image
        cv2.imshow("Game", imgBG)
        if (currentState == 'GAME_SCORES'):
            cv2.waitKey(1000)
    else:
        imgAI = cv2.imread(f'Resources/{gameRandomNumber}.png', cv2.IMREAD_UNCHANGED)
        imgBG = cvzone.overlayPNG(imgBG, imgAI, (69, 181))
        cv2.imshow("Game", imgBG)

# Function to display game scores round by round
def gameScores():
    global gameRandomNumber, gameScoreProgressBarCounter, currentState, gameRandomNumber, currentRound, roundCount
    gameScoreProgressBarCounter += 1
    imgBG = cv2.imread("Resources/game_score_bg.png")

    # Display the current round, PC winnings, and player winnings on the image
    cv2.putText(imgBG, str(currentRound), (495, 60), cv2.FONT_HERSHEY_DUPLEX, 2, (190, 183, 36), 2)
    cv2.putText(imgBG, str(pcWinnings), (90, 400), cv2.FONT_HERSHEY_DUPLEX, 10, (190, 183, 36), 10)
    cv2.putText(imgBG, str(playerWinnings), (600, 400), cv2.FONT_HERSHEY_DUPLEX, 10, (190, 183, 36), 10)

    # Display the game score progress bar based on the gameScoreProgressBarCounter
    cv2.putText(imgBG, gameScoreProgressBarCounter * '|', (130, 480), cv2.FONT_HERSHEY_DUPLEX, 1, (190, 183, 36), 2)
    cv2.imshow("Game", imgBG)

    if (gameScoreProgressBarCounter > 79):  # If the game score progress bar is complete
        gameScoreProgressBarCounter = 0
        gameRandomNumber = 0
        if (roundCount > currentRound):     # If there are more rounds to play
            currentState = 'GAME'
        else:
            currentState = 'FINAL_SCORES'   # Move to the final scores state

# Function to display final scores
def finalScores():
    global gameRandomNumber, gameScoreProgressBarCounter, currentState, gameRandomNumber, currentRound, roundCount, playerWinnings, pcWinnings
    gameScoreProgressBarCounter += 1
    defaultBackground = "draw"  # Default background image used when tied

    if pcWinnings > playerWinnings:  # If PC has more winnings than the player
        defaultBackground = 'lost'
    elif pcWinnings < playerWinnings:    # If player has more winnings than PC
        defaultBackground = 'won'

    imgBG = cv2.imread("Resources/" + defaultBackground + ".png")
    # cv2.putText(imgBG, gameScoreProgressBarCounter * '|', (75, 460), cv2.FONT_HERSHEY_DUPLEX, 1, (190, 183, 36), 2)
    cv2.imshow("Game", imgBG)   # Show the final scores image

    if (gameScoreProgressBarCounter > 79):   # If the game score progress bar is complete
        gameScoreProgressBarCounter = 0
        gameRandomNumber = 0
        playerWinnings = 0
        pcWinnings = 0
        currentRound = 0
        currentState = 'HOME'   # Move to the home state


while True:
    # Video frame reading process.
    videoReadingStatus, frame = cap.read()

    # Video reading thread has been slept in here.
    key = cv2.waitKey(1)

    # Reading status checked in here.
    if videoReadingStatus:
        # Scaling the captured frame.
        imgScaled = cv2.resize(frame, (0, 0), None, 0.54, 0.54)
        imgScaled = imgScaled[:, 43:303]

        # Identifying the hands in the frame.
        hands, frame = detector.findHands(imgScaled)
        # states of the game
        if currentState == 'HOME':
            handleHome(hands)
        elif currentState == 'ROUNDS_COUNT':
            roundsCount(hands)
        elif currentState == 'VERIFY_ROUNDS':
            verifyRounds(hands)
        elif currentState == 'GAME':
            game(hands)
        elif currentState == 'GAME_SCORES':
            gameScores()
        elif currentState == 'FINAL_SCORES':
            finalScores()
    else:
        print("Some error occurred with camera process. Please check and try again.")
