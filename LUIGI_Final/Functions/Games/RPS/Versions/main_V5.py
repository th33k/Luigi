import random
import cv2
import pygame
from cvzone.HandTrackingModule import HandDetector
import cvzone

class RockPaperScissorsGame:
    def __init__(self):
        self.detector = HandDetector(maxHands=2)
        self.cap = cv2.VideoCapture(0)
        self.cap.set(3, 480)
        self.cap.set(4, 320)
        
        self.imgScaled = None
        self.gameRandomNumber = 0
        self.currentState = 'HOME'
        self.currentRound = 0
        self.playerWinnings = 0
        self.pcWinnings = 0
        self.gameScoreProgressBarCounter = 0
        
        pygame.init()
        pygame.mixer.init()

    def playSound(self):
        filename = 'Resources/notify.wav'
        # Add implementation for playing sound

    def fingerGestureDetection(self, fingers):
        gestures = {
            (0, 0, 0, 0, 0): 1,  # Rock
            (1, 1, 1, 1, 1): 2,  # Paper
            (0, 1, 1, 0, 0): 3,  # Scissors
        }
        return gestures.get(tuple(fingers), 0)

    def identifyFingerGesture(self, fingers):
        identifiedGesture = self.fingerGestureDetection(fingers)
        # Implement logic to identify correct user gesture and avoid accidental gestures
        return identifiedGesture

    def game(self, hands):
        imgBG = cv2.imread("Resources/game_bg.png")
        if len(hands) >= 1:
            verifyUserInput = self.identifyFingerGesture(self.detector.fingersUp(hands[0]))
            if verifyUserInput > 0:
                self.currentRound += 1
                self.gameRandomNumber = random.randint(1, 3)
                if (verifyUserInput - self.gameRandomNumber) % 3 == 1:
                    self.playerWinnings += 1
                elif (verifyUserInput - self.gameRandomNumber) % 3 == 2:
                    self.pcWinnings += 1
                self.currentState = 'GAME_SCORES'
            imgAI = cv2.imread(f'Resources/{self.gameRandomNumber}.png', cv2.IMREAD_UNCHANGED)
            imgBG = cvzone.overlayPNG(imgBG, imgAI, (69, 181))
            cv2.imshow("Game", imgBG)
            if self.currentState == 'GAME_SCORES':
                cv2.waitKey(1000)
        else:
            imgAI = cv2.imread(f'Resources/{self.gameRandomNumber}.png', cv2.IMREAD_UNCHANGED)
            imgBG = cvzone.overlayPNG(imgBG, imgAI, (69, 181))
            cv2.imshow("Game", imgBG)

    def gameScores(self):
        imgBG = cv2.imread("Resources/game_score_bg.png")
        self.gameScoreProgressBarCounter += 1
        cv2.putText(imgBG, str(self.currentRound), (495, 60), cv2.FONT_HERSHEY_DUPLEX, 2, (190, 183, 36), 2)
        cv2.putText(imgBG, str(self.pcWinnings), (90, 400), cv2.FONT_HERSHEY_DUPLEX, 10, (190, 183, 36), 10)
        cv2.putText(imgBG, str(self.playerWinnings), (600, 400), cv2.FONT_HERSHEY_DUPLEX, 10, (190, 183, 36), 10)
        cv2.putText(imgBG, self.gameScoreProgressBarCounter * '|', (130, 480), cv2.FONT_HERSHEY_DUPLEX, 1, (190, 183, 36), 2)
        cv2.imshow("Game", imgBG)
        if self.gameScoreProgressBarCounter >= 80:
            self.gameScoreProgressBarCounter = 0
            if self.roundCount > self.currentRound:
                self.currentState = 'GAME'
            else:
                self.currentState = 'FINAL_SCORES'

    def finalScores(self):
        defaultBackground = "draw"
        if self.pcWinnings > self.playerWinnings:
            defaultBackground = 'lost'
        elif self.pcWinnings < self.playerWinnings:
            defaultBackground = 'won'
        imgBG = cv2.imread(f"Resources/{defaultBackground}.png")
        cv2.imshow("Game", imgBG)
        if self.gameScoreProgressBarCounter >= 80:
            self.gameScoreProgressBarCounter = 0
            self.playerWinnings = 0
            self.pcWinnings = 0
            self.currentRound = 0
            self.currentState = 'HOME'

    def main(self):
        while True:
            videoReadingStatus, frame = self.cap.read()
            key = cv2.waitKey(1)
            if videoReadingStatus:
                self.imgScaled = cv2.resize(frame, (0, 0), None, 0.54, 0.54)
                self.imgScaled = self.imgScaled[:, 43:303]
                hands, frame = self.detector.findHands(self.imgScaled)
                if self.currentState == 'HOME':
                    pygame.mixer.music.load('Resources/RPS.mp3')
                    pygame.mixer.music.play()
                    self.currentState = 'GAME'
                elif self.currentState == 'GAME':
                    pygame.mixer.music.load('Resources/RPS.mp3')
                    pygame.mixer.music.play()
                    self.game(hands)
                elif self.currentState == 'GAME_SCORES':
                    self.gameScores()
                elif self.currentState == 'FINAL_SCORES':
                    self.finalScores()
                if self.currentState == 'HOME':
                    break
            else:
                print("Some error occurred with camera process. Please check and try again.")
                break
        pygame.quit()

if __name__ == "__main__":
    rps_game = RockPaperScissorsGame()
    rps_game.main()
