"""
This script controls a car with a Raspberry Pi, using a servo motor for the front wheels and left-right DC motors for the back wheels.
It defines a movement function `move` that performs specific actions:
1. Moves the servo to 135 degrees from 90 degrees and moves the DC motors forward for 0.5 seconds, then reverses for 0.5 seconds.
2. Resets the servo to 90 degrees.
3. Moves the servo to 45 degrees from 90 degrees and moves the DC motors forward for 0.5 seconds, then reverses for 0.5 seconds.
4. Resets the servo to 90 degrees.

The script sets up the necessary GPIO pins and PWM for the servo motor, and it ensures proper cleanup of GPIO resources after execution.
"""

import RPi.GPIO as GPIO
import time

# Pin Definitions
SERVO_PIN = 23      # GPIO pin connected to the servo motor
LEFT_MOTOR_FORWARD_PIN = 27
LEFT_MOTOR_BACKWARD_PIN = 22
RIGHT_MOTOR_FORWARD_PIN = 23
RIGHT_MOTOR_BACKWARD_PIN = 24

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(SERVO_PIN, GPIO.OUT)
GPIO.setup(LEFT_MOTOR_FORWARD_PIN, GPIO.OUT)
GPIO.setup(LEFT_MOTOR_BACKWARD_PIN, GPIO.OUT)
GPIO.setup(RIGHT_MOTOR_FORWARD_PIN, GPIO.OUT)
GPIO.setup(RIGHT_MOTOR_BACKWARD_PIN, GPIO.OUT)

# Set the PWM frequency to 50Hz (20ms period)
pwm = GPIO.PWM(SERVO_PIN, 50)
pwm.start(0)

# Function to set the servo angle
def set_servo_angle(angle):
    duty_cycle = (angle / 18.0) + 2.5
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.1)
    pwm.ChangeDutyCycle(0)

# Function to move the car as per the specified actions
def move():
    # Move servo to 135 degrees from 90 degrees and move DC motors forward
    set_servo_angle(135)
    GPIO.output(LEFT_MOTOR_FORWARD_PIN, GPIO.HIGH)
    GPIO.output(RIGHT_MOTOR_FORWARD_PIN, GPIO.HIGH)
    time.sleep(0.5)
    
    # Reverse DC motors
    GPIO.output(LEFT_MOTOR_FORWARD_PIN, GPIO.LOW)
    GPIO.output(RIGHT_MOTOR_FORWARD_PIN, GPIO.LOW)
    GPIO.output(LEFT_MOTOR_BACKWARD_PIN, GPIO.HIGH)
    GPIO.output(RIGHT_MOTOR_BACKWARD_PIN, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(LEFT_MOTOR_BACKWARD_PIN, GPIO.LOW)
    GPIO.output(RIGHT_MOTOR_BACKWARD_PIN, GPIO.LOW)
    
    # Reset servo to 90 degrees
    set_servo_angle(90)
    time.sleep(0.5)
    
    # Move servo to 45 degrees from 90 degrees and move DC motors forward
    set_servo_angle(45)
    GPIO.output(LEFT_MOTOR_FORWARD_PIN, GPIO.HIGH)
    GPIO.output(RIGHT_MOTOR_FORWARD_PIN, GPIO.HIGH)
    time.sleep(0.5)
    
    # Reverse DC motors
    GPIO.output(LEFT_MOTOR_FORWARD_PIN, GPIO.LOW)
    GPIO.output(RIGHT_MOTOR_FORWARD_PIN, GPIO.LOW)
    GPIO.output(LEFT_MOTOR_BACKWARD_PIN, GPIO.HIGH)
    GPIO.output(RIGHT_MOTOR_BACKWARD_PIN, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(LEFT_MOTOR_BACKWARD_PIN, GPIO.LOW)
    GPIO.output(RIGHT_MOTOR_BACKWARD_PIN, GPIO.LOW)
    
    # Reset servo to 90 degrees
    set_servo_angle(90)

def Rock_Dance():
    try:
        move()
    finally:
        # Cleanup GPIO
        pwm.stop()
        GPIO.cleanup()

if __name__ == "__main__":
    Rock_Dance()
