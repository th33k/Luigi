import sys
import os
import subprocess
import threading
import time
import webview
import RPi.GPIO as GPIO
from bluetooth import *

# GPIO Pin Definitions
TOUCH_PIN = 5  # GPIO pin connected to the touch sensor
LED_PIN = 13    # GPIO pin for controlling the horn
LED2_PIN = 2    # GPIO pin for controlling the headlight

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TOUCH_PIN, GPIO.IN)
GPIO.setup(LED_PIN, GPIO.OUT)
GPIO.setup(LED2_PIN, GPIO.OUT)

DOUBLE_TAP_INTERVAL = 0.5
last_tap_time = 0
tap_count = 0

# Bluetooth Constants
ESP32_MAC_ADDRESS = "30:C9:22:31:BD:0A"  # MAC address of the ESP32
SERVICE_UUID = "00001101-0000-1000-8000-00805F9B34FB"  # SPP (Serial Port Profile) UUID
port = 1  # RFCOMM port number, typically 1 for SPP

# Define GPIO pins for the motor
in1 = 27
in2 = 21
en = 17

# Define the GPIO pin number for the servo signal
servo_pin = 22

# Setup motor GPIO pins
GPIO.setup(in1, GPIO.OUT)
GPIO.setup(in2, GPIO.OUT)
GPIO.setup(en, GPIO.OUT)
GPIO.output(in1, GPIO.LOW)
GPIO.output(in2, GPIO.LOW)
pwm_motor = GPIO.PWM(en, 1000)
pwm_motor.start(50)

# Setup servo GPIO pin
GPIO.setup(servo_pin, GPIO.OUT)
pwm_servo = GPIO.PWM(servo_pin, 50)
pwm_servo.start(0)

# Function to control LED and horn/headlight
def led_combined(horn, headlight):
    if horn and headlight:
        GPIO.output(LED_PIN, GPIO.HIGH)   # Turn on the horn
        GPIO.output(LED2_PIN, GPIO.HIGH)  # Turn on the headlight
        print("Horn and HeadLight are ON")
    elif horn:
        GPIO.output(LED_PIN, GPIO.HIGH)   # Turn on the horn
        GPIO.output(LED2_PIN, GPIO.LOW)   # Turn off the headlight
        print("Horn is ON, HeadLight is OFF")
    elif headlight:
        GPIO.output(LED_PIN, GPIO.LOW)    # Turn off the horn
        GPIO.output(LED2_PIN, GPIO.HIGH)  # Turn on the headlight
        print("Horn is OFF, HeadLight is ON")
    else:
        GPIO.output(LED_PIN, GPIO.LOW)    # Turn off the horn
        GPIO.output(LED2_PIN, GPIO.LOW)   # Turn off the headlight
        print("Horn and HeadLight are OFF")

# Function to set the motor direction based on received number
def set_motor_from_received_number(number):
    global pwm_motor
    if number == 4 or number == 5 or number == 6:
        print("Motor forward")
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)
    elif number == 3 or number == 7 or number == 8:
        print("Motor backward")
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.HIGH)
    elif number == 1 or number == 2 or number == 0:
        print("Motor not moved")
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.LOW)
    else:
        print("Invalid motor command received, no action taken.")

# Function to set the servo angle based on received number
def set_servo_from_received_number(number):
    global pwm_servo
    if number == 2 or number == 5 or number == 7:
        print("Turn left")
        set_servo_angle(45)
    elif number == 1 or number == 8 or number == 6:
        print("Turn right")
        set_servo_angle(135)
    elif number == 3 or number == 4:
        print("Move straight")
        set_servo_angle(90)
    else:
        print("Invalid servo command received, no action taken.")

# Function to set the servo angle
def set_servo_angle(angle):
    global pwm_servo
    duty_cycle = (angle / 18) + 2.5
    pwm_servo.ChangeDutyCycle(duty_cycle)
    time.sleep(0.01)
    pwm_servo.ChangeDutyCycle(0)  # Turn off the signal after setting the angle

# Function to handle Bluetooth data and control motor/servo/LEDs
def bluetooth_loop(sock):
    try:
        while True:
            data = sock.recv(1024)
            if not data:
                break
            data_str = data.decode().strip()
            parts = data_str.split(',')
            
            if len(parts) == 3:
                command = int(parts[0])
                horn = int(parts[1])
                headlight = int(parts[2])
                print(f"Command: {command}, Horn: {horn}, Headlight: {headlight}")
                
                set_servo_from_received_number(command)
                set_motor_from_received_number(command)
                led_combined(horn, headlight)
    except Exception as e:
        print(f"Error in Bluetooth loop: {e}")
    finally:
        sock.close()

# Function to start the webview
def start_webview():
    global window
    window = webview.create_window('LUIGI', '/home/pi/Desktop/LUIGI_Final/HTML/drive.html', width=480, height=320)
    webview.start()

# Start double tap detection in a separate thread
def detect_double_tap():
    global last_tap_time, tap_count
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
                    print("Double tap detected! Stopping sensor readings.")
                    tap_count = 0  # Reset tap count after a double tap
                    global client_sock
                    client_sock.close()  # Close Bluetooth socket

                    # Close the webview window
                    if window:
                        window.destroy()

                    # Cleanup GPIO
                    GPIO.cleanup()

                    subprocess.run(['python', '/home/pi/Desktop/LUIGI_Final/Function.py'])
                    os._exit(0)  # Terminate the script

                # Debounce delay
                while GPIO.input(TOUCH_PIN) == GPIO.HIGH:
                    time.sleep(0.01)

            time.sleep(0.01)

    except KeyboardInterrupt:
        print("Exiting program")
    finally:
        GPIO.cleanup()

if __name__ == "__main__":
    try:
        # Bluetooth client setup
        client_sock = BluetoothSocket(RFCOMM)
        client_sock.connect((ESP32_MAC_ADDRESS, port))
        print(f"Connected to ESP32 at MAC address {ESP32_MAC_ADDRESS}")

        # Start double tap detection in a separate thread
        tap_thread = threading.Thread(target=detect_double_tap)
        tap_thread.start()

        # Start the Bluetooth loop in a separate thread
        bluetooth_thread = threading.Thread(target=bluetooth_loop, args=(client_sock,))
        bluetooth_thread.start()

        # Start the webview in the main thread
        start_webview()

    except Exception as e:
        print(f"Error: {e}")
        GPIO.cleanup()
