import RPi.GPIO as GPIO
import time
import subprocess
import webview
import threading
import os
import pygame

# Pin Definitions
TOUCH_PIN = 5     # GPIO pin connected to the touch sensor for double tap detection
TOUCH_PIN_6 = 6    # GPIO pin connected to additional touch sensor 6
TOUCH_PIN_13 = 13  # GPIO pin connected to additional touch sensor 13
TOUCH_PIN_19 = 19  # GPIO pin connected to additional touch sensor 19
ULTRASONIC_TRIG = 20  # GPIO pin connected to ultrasonic sensor (TRIG)
ULTRASONIC_ECHO = 21  # GPIO pin connected to ultrasonic sensor (ECHO)

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TOUCH_PIN, GPIO.IN)
GPIO.setup(TOUCH_PIN_6, GPIO.IN)
GPIO.setup(TOUCH_PIN_13, GPIO.IN)
GPIO.setup(TOUCH_PIN_19, GPIO.IN)
GPIO.setup(ULTRASONIC_TRIG, GPIO.OUT)
GPIO.setup(ULTRASONIC_ECHO, GPIO.IN)

# Define GPIO pins for servo
servo_pin = 23
GPIO.setup(servo_pin, GPIO.OUT)

# Set the PWM frequency to 50Hz (20ms period)
pwm = GPIO.PWM(servo_pin, 50)
pwm.start(0)

# Initialize Pygame and load the sound files
pygame.init()
pygame.mixer.init()

main_video_path = 'HTML/Video/Eyes_Blink_Blue.mp4'
ultrasonic_video_path = 'HTML/Video/Angry_Red.mp4'

additional_video_paths = {
    TOUCH_PIN_6: 'HTML/Video/Compassionate_Blue.mp4',
    TOUCH_PIN_13: 'HTML/Video/Happy_Green.mp4',
    TOUCH_PIN_19: 'HTML/Video/Love_Red.mp4'
}

sound = pygame.mixer.Sound("/home/pi/Desktop/LUIGI_Final/HTML/Audio/angry.wav")

additional_sounds = {
    TOUCH_PIN_6: pygame.mixer.Sound("/home/pi/Desktop/LUIGI_Final/HTML/Audio/emotion_compassion.wav"),
    TOUCH_PIN_13: pygame.mixer.Sound("/home/pi/Desktop/LUIGI_Final/HTML/Audio/emotion_happy.wav"),
    TOUCH_PIN_19: pygame.mixer.Sound("/home/pi/Desktop/LUIGI_Final/HTML/Audio/emotion_love.wav")
}

# Flags to track if the sounds are playing
sound_playing = False
additional_sound_playing = {pin: False for pin in additional_sounds.keys()}

# Variable to track current video in webview
current_video_playing = main_video_path

# Function to set the servo angle
def set_servo_angle(angle):
    duty_cycle = (angle / 18.0) + 2.5
    pwm.ChangeDutyCycle(duty_cycle)
    time.sleep(0.1)
    pwm.ChangeDutyCycle(0)

# Function to test the ultrasonic sensor
def test_ultrasonic_sensor():
    GPIO.output(ULTRASONIC_TRIG, False)
    time.sleep(0.5)  # Allow sensor to settle

    GPIO.output(ULTRASONIC_TRIG, True)
    time.sleep(0.01)  # 10us pulse
    GPIO.output(ULTRASONIC_TRIG, False)

    start_time = time.time()
    stop_time = time.time()

    while GPIO.input(ULTRASONIC_ECHO) == 0:
        start_time = time.time()

    while GPIO.input(ULTRASONIC_ECHO) == 1:
        stop_time = time.time()

    elapsed_time = stop_time - start_time
    distance = (elapsed_time * 34300) / 2  # Speed of sound is 343 m/s
    return distance

# Time interval for detecting double tap (in seconds)
DOUBLE_TAP_INTERVAL = 0.5

# Variables to keep track of taps and sensor state
last_tap_time = 0
tap_count = 0
sensor_enabled = True

game_process = None
window = None
sound_thread = None

# Function to start the webview
def start_webview():
    global window
    window = webview.create_window('LUIGI', 'Home.html', width=480, height=320 ,fullscreen=True)
    webview.start()

# Function to detect double tap on touch sensor
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
                    global sensor_enabled
                    sensor_enabled = False  # Disable sensor readings

                    # Close the webview window
                    if window:
                        webview.windows[0].destroy()

                    # Exit the script after running another script
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

# Function to control the servo
def move_servo():
    global game_process, sensor_enabled, current_video_playing
    try:
        while True:
            if sensor_enabled:
                dist = test_ultrasonic_sensor()

                if dist > 10:
                    print(f"Distance: {dist} cm - Moving servo")

                    set_servo_angle(38)
                    time.sleep(0.03)
                    set_servo_angle(90)
                    time.sleep(0.03)
                    set_servo_angle(142)
                    time.sleep(0.03)
                    set_servo_angle(90)
                    time.sleep(0.03)

                    # Start the sound thread if not already running and sound is not already playing
                    global sound_thread, sound_playing
                    if sound_thread is None or not sound_thread.is_alive():
                        if not sound_playing:
                            sound_thread = threading.Thread(target=play_sound)
                            sound_thread.start()

                    # Change the video in the webview for ultrasonic condition
                    if current_video_playing != ultrasonic_video_path:
                        webview.windows[0].evaluate_js(f"setVideoSource('{ultrasonic_video_path}')")
                        current_video_playing = ultrasonic_video_path
                else:
                    print(f"Distance: {dist} cm - Stopping servo")
                    pwm.ChangeDutyCycle(0)

                    # Stop the sound if it's playing
                    if sound_playing:
                        stop_sound()

                    # Change the video back to main video in the webview
                    if current_video_playing != main_video_path:
                        webview.windows[0].evaluate_js(f"setVideoSource('{main_video_path}')")
                        current_video_playing = main_video_path

            else:
                time.sleep(0.5)  # Wait for half a second before checking again

    except KeyboardInterrupt:
        print("Measurement stopped by user")
    finally:
        pwm.stop()
        GPIO.cleanup()

# Function to handle additional touch sensors
def handle_additional_touch(pin):
    global additional_sound_playing
    try:
        while True:
            if GPIO.input(pin) == GPIO.HIGH:
                if not additional_sound_playing[pin]:
                    print(f"Additional touch sensor on pin {pin} activated!")

                    # Change the video in the webview based on the touch sensor activated
                    video_path = additional_video_paths.get(pin, main_video_path)
                    webview.windows[0].evaluate_js(f"setVideoSource('{video_path}')")

                    # Play the additional sound for 8 seconds
                    additional_sound_playing[pin] = True
                    additional_sounds[pin].play()
                    start_time = time.time()
                    while time.time() - start_time < 8:
                        time.sleep(0.1)
                    additional_sounds[pin].stop()
                    additional_sound_playing[pin] = False

                    # Wait for 10 seconds before returning to main video
                    time.sleep(1)
                    webview.windows[0].evaluate_js(f"setVideoSource('{main_video_path}')")

                # Debounce delay
                while GPIO.input(pin) == GPIO.HIGH:
                    time.sleep(0.01)
            time.sleep(0.01)
    except KeyboardInterrupt:
        print("Exiting program")
    finally:
        GPIO.cleanup()

# Function to play the sound
def play_sound():
    global sound_playing
    sound_playing = True
    sound.play()
    while pygame.mixer.get_busy():
        time.sleep(0.1)  # Check every 0.1 seconds if sound is still playing
    sound_playing = False

# Function to stop the sound
def stop_sound():
    global sound_playing
    sound.stop()
    sound_playing = False

if __name__ == "__main__":
    try:
        # Start threads for double tap detection, servo control, and additional touch sensors
        detection_thread = threading.Thread(target=detect_double_tap)
        detection_thread.start()

        servo_thread = threading.Thread(target=move_servo)
        servo_thread.start()

        additional_touch_thread_6 = threading.Thread(target=handle_additional_touch, args=(TOUCH_PIN_6,))
        additional_touch_thread_6.start()

        additional_touch_thread_13 = threading.Thread(target=handle_additional_touch, args=(TOUCH_PIN_13,))
        additional_touch_thread_13.start()

        additional_touch_thread_19 = threading.Thread(target=handle_additional_touch, args=(TOUCH_PIN_19,))
        additional_touch_thread_19.start()

        # Start the webview
        start_webview()

        # Wait for the threads to finish (although they will run indefinitely until Ctrl+C is pressed)
        detection_thread.join()
        servo_thread.join()
        additional_touch_thread_6.join()
        additional_touch_thread_13.join()
        additional_touch_thread_19.join()

    except KeyboardInterrupt:
        print("Exiting program")
    finally:
        # Clean up resources
        pygame.mixer.quit()
        pygame.quit()
        GPIO.cleanup()
