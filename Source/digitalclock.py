import webview
import tkinter as tk
import RPi.GPIO as GPIO
import subprocess
import os
import time
import threading


# Pin Definitions
TOUCH_PIN = 5  # GPIO pin connected to the touch sensor

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TOUCH_PIN, GPIO.IN)

# Time interval for detecting double tap (in seconds)
DOUBLE_TAP_INTERVAL = 0.5

# Variables to keep track of taps and sensor state
last_tap_time = 0
tap_count = 0
sensor_enabled = True

def detect_double_tap():
    global last_tap_time, tap_count, window
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
                    # Close the webview window
                    webview.windows[0].destroy()

                    subprocess.run(['python', '/home/pi/Desktop/Luigi/Function.py'])
                    os._exit(0)  # Terminate the script

                # Debounce delay
                while GPIO.input(TOUCH_PIN) == GPIO.HIGH:
                    time.sleep(0.01)

            time.sleep(0.01)
    except KeyboardInterrupt:
        print("Exiting program")
    finally:
        GPIO.cleanup()

def start_webview():
    window = webview.create_window('Digital Clock', 'digitalclock.html', width=480, height=320,fullscreen=True)
    webview.start()

if __name__ == "__main__":
     # Start the double tap detection in a separate thread
    detection_thread = threading.Thread(target=detect_double_tap)
    detection_thread.start()
    
    start_webview()
    
    # Wait for the detection thread to finish (although it will run indefinitely until Ctrl+C is pressed)
    detection_thread.join()
