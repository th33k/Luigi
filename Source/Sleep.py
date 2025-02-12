import webview
import time
import threading
import subprocess
import os
import RPi.GPIO as GPIO
import smbus
import math
import pygame

# Initialize Pygame mixer
pygame.mixer.init()

# GPIO Pin Definitions
TOUCH_PIN = 5  # GPIO pin connected to the touch sensor

# MPU6050 Register addresses
DEVICE_ADDRESS = 0x68  # MPU6050 I2C Address
PWR_MGMT_1 = 0x6B      # Power management register
ACCEL_XOUT_H = 0x3B    # Accelerometer data registers

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TOUCH_PIN, GPIO.IN)

# Initialize I2C bus
bus = smbus.SMBus(1)  # 1 indicates /dev/i2c-1

# Wake up MPU6050 and set it to accelerometer mode
bus.write_byte_data(DEVICE_ADDRESS, PWR_MGMT_1, 0)

# Time interval for detecting double tap (in seconds)
DOUBLE_TAP_INTERVAL = 0.5

# Variables to keep track of taps and sensor state
last_tap_time = 0
tap_count = 0
sensor_enabled = True

# Variable to control the webview window
window = None

print("Touch sensor double-tap and shake detection. Press Ctrl+C to exit")

def start_webview():
    global window
    window = webview.create_window('LUIGI', 'sleep.html', width=480, height=320,fullscreen=True)
    webview.start()

# Function to read accelerometer data
def read_accel():
    data = bus.read_i2c_block_data(DEVICE_ADDRESS, ACCEL_XOUT_H, 6)
    raw_accel = [(data[i] << 8) + data[i+1] for i in range(0, 6, 2)]
    accel = [a / 16384.0 for a in raw_accel]  # 16384 LSB/g according to datasheet
    return accel

def calculate_velocity(accel1, accel2, dt):
    velocity = [(accel2[i] - accel1[i]) / dt for i in range(3)]
    return velocity

def detect_shake(min_velocity=3.0):
    accel1 = read_accel()
    time.sleep(0.1)  # Adjust delay as needed
    accel2 = read_accel()
    
    # Assuming a fixed time interval of 0.1 seconds (adjust as per your actual sampling rate)
    dt = 0.1
    velocity = calculate_velocity(accel1, accel2, dt)
    
    # Calculate magnitude of velocity vector
    velocity_magnitude = math.sqrt(sum([v**2 for v in velocity]))
    
    if velocity_magnitude > min_velocity:
        return True
    else:
        return False

# Function to play video in webview for a specific duration
def play_video_for_duration(video_src, duration):
    global window
    if window:
        window.evaluate_js(f'showVideo("{video_src}");')
        time.sleep(duration)
        window.evaluate_js('hideVideo();')

# Function to play audio file in a thread
def play_audio_in_thread(audio_file, duration):
    pygame.mixer.music.load(audio_file)
    pygame.mixer.music.play()

    # Wait for the specified duration while audio plays
    time.sleep(duration)

    # Stop audio playback
    pygame.mixer.music.stop()

def execute_file(file_path):
    subprocess.run(["python3", file_path], check=True)

# Function to detect shake in a separate thread
def shake_detection_thread():
    shake_count = 0
    required_shakes = 2
    global sensor_enabled  # Add this line to use the global variable

    try:
        while True:
            if not sensor_enabled:  # Check if sensor readings are disabled
                print("Shake detection stopped.")
                break
            if detect_shake():
                shake_count += 1
                if shake_count >= required_shakes:
                    print("Shake detected! Playing video and audio for 11 seconds.")
                    
                    # Start video playback in a thread
                    video_thread = threading.Thread(target=play_video_for_duration, args=("Video/Wake_Red.mp4", 11))
                    video_thread.start()
                    
                    # Start audio playback in a thread
                    audio_thread = threading.Thread(target=play_audio_in_thread, args=("/home/pi/Desktop/Luigi/HTML/Audio/yawn.wav", 11))
                    audio_thread.start()

                    # Wait for video and audio threads to finish
                    video_thread.join()
                    audio_thread.join()

                    # Close the webview window
                    if window:
                        webview.windows[0].destroy()
                    
                    # Run another Python script
                    subprocess.run(['python', '/home/pi/Desktop/Luigi/Home.py'])
                    os._exit(0)  # Terminate the script

                    shake_count = 0  # Reset shake count
            else:
                print("No shake detected.")
                shake_count = 0  # Reset shake count if no shake is detected
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("Exiting...")

def detect_double_tap():
    global last_tap_time, tap_count, window, sensor_enabled  # Add sensor_enabled here
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
                    sensor_enabled = False  # Disable sensor readings

                    # Close the webview window
                    if window:
                        webview.windows[0].destroy()

                    # Run another Python script
                    subprocess.run(['python', '/home/pi/Desktop/Luigi/Home.py'])
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
    # Start the shake detection in a separate thread
    shake_thread = threading.Thread(target=shake_detection_thread)
    shake_thread.start()

    # Start the double tap detection in a separate thread
    detection_thread = threading.Thread(target=detect_double_tap)
    detection_thread.start()

    # Start the webview
    start_webview()

    try:
        # Keep the main thread running indefinitely
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("Exiting program")
        sys.exit(0)
