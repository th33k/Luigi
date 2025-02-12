import socket
import RPi.GPIO as GPIO
import subprocess
import os
import webview
import time
import threading

# GPIO Pin Definitions
TOUCH_PIN = 5  # GPIO pin connected to the touch sensor
TRIG_PIN = 16  # GPIO pin connected to the ultrasonic sensor trigger
ECHO_PIN = 12  # GPIO pin connected to the ultrasonic sensor echo

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TOUCH_PIN, GPIO.IN)
GPIO.setup(TRIG_PIN, GPIO.OUT)
GPIO.setup(ECHO_PIN, GPIO.IN)

LED_PIN = 3  # GPIO pin for controlling the horn
GPIO.setup(LED_PIN, GPIO.OUT)

LED2_PIN = 2  # GPIO pin for controlling the headlight
GPIO.setup(LED2_PIN, GPIO.OUT)

DOUBLE_TAP_INTERVAL = 0.5

last_tap_time = 0
tap_count = 0

UDP_IP = "192.168.137.30"  # The IP that is printed in the serial monitor from the ESP32
SHARED_UDP_PORT = 4210
sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # Internet  # UDP
sock.connect((UDP_IP, SHARED_UDP_PORT))

# Define GPIO pins for the motor
in1 = 17
in2 = 18
en = 27

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

# Flag to indicate if safety action is active
safety_active = False

# Function to control LED and horn/headlight
def led_combined(horn, headlight):
    if horn and headlight:
        GPIO.output(LED_PIN, GPIO.HIGH)  # Turn on the horn
        GPIO.output(LED2_PIN, GPIO.HIGH)  # Turn on the headlight
        print("Horn and HeadLight are ON")
    elif horn:
        GPIO.output(LED_PIN, GPIO.HIGH)  # Turn on the horn
        GPIO.output(LED2_PIN, GPIO.LOW)  # Turn off the headlight
        print("Horn is ON, HeadLight is OFF")
    elif headlight:
        GPIO.output(LED_PIN, GPIO.LOW)  # Turn off the horn
        GPIO.output(LED2_PIN, GPIO.HIGH)  # Turn on the headlight
        print("Horn is OFF, HeadLight is ON")
    else:
        GPIO.output(LED_PIN, GPIO.LOW)  # Turn off the horn
        GPIO.output(LED2_PIN, GPIO.LOW)  # Turn off the headlight
        print("Horn and HeadLight are OFF")

# Function to set the motor direction based on received number
def set_motor_from_received_number(number):
    global safety_active
    if safety_active:
        return
    if number == 4 or number == 5 or number == 6:
        print("Motor forward")
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.HIGH)
    elif number == 3 or number == 7 or number == 8:
        print("Motor backward")
        GPIO.output(in1, GPIO.HIGH)
        GPIO.output(in2, GPIO.LOW)
    elif number == 1 or number == 2 or number == 0:
        print("Motor not moved")
        GPIO.output(in1, GPIO.LOW)
        GPIO.output(in2, GPIO.LOW)
    else:
        print("Invalid motor command received, no action taken.")

# Function to set the servo angle based on received number
def set_servo_from_received_number(number):
    if number == 2 or number == 5 or number == 7:
        print("left")
        set_servo_angle(45)  # Turn left (45 degrees)
    elif number == 1 or number == 8 or number == 6:
        set_servo_angle(135)  # Turn right (135 degrees)
        print("right")
    elif number == 3 or number == 4:
        set_servo_angle(90)  # Move to neutral (90 degrees)
        print("straight")
    else:
        print("Invalid servo command received, no action taken.")

# Function to set the servo angle
def set_servo_angle(angle):
    duty_cycle = (angle / 18) + 2.5
    pwm_servo.ChangeDutyCycle(duty_cycle)
    time.sleep(0.01)
    pwm_servo.ChangeDutyCycle(0)  # Turn off the signal after setting the angle

# Function to measure distance using ultrasonic sensor
def measure_distance():
    # Send a 10us pulse to trigger the sensor
    GPIO.output(TRIG_PIN, True)
    time.sleep(0.001)
    GPIO.output(TRIG_PIN, False)

    # Wait for the echo pin to go high and record the start time
    while GPIO.input(ECHO_PIN) == 0:
        start_time = time.time()

    # Wait for the echo pin to go low and record the end time
    while GPIO.input(ECHO_PIN) == 1:
        end_time = time.time()

    # Calculate the distance based on the duration of the echo pulse
    duration = end_time - start_time
    distance = (duration * 34300) / 2  # Speed of sound is 34300 cm/s

    return distance

# Function to handle UDP data and control motor/servo/LEDs
def udp_loop():
    while True:
        data = sock.recv(2048)
        data_str = data.decode().strip()
        parts = data_str.split(',')
        
        if len(parts) == 3:
            command = int(parts[0])
            horn = int(parts[1])
            headlight = int(parts[2])

            print(f"Command: {command}, Horn: {horn}, Headlight: {headlight}")

            set_servo_from_received_number(command)
            set_motor_from_received_number(command)
            led_combined(horn, headlight)  # Call the combined function

# Function to monitor ultrasonic sensor and move motor backward if obstacle detected
def ultrasonic_monitor():
    global safety_active
    while True:
        distance = measure_distance()
        print(f"Distance: {distance} cm")

        if distance < 5 and not safety_active:
            print("Obstacle detected! Moving motor backward.")
            safety_active = True
            GPIO.output(in1, GPIO.HIGH)
            GPIO.output(in2, GPIO.LOW)
            time.sleep(2)
            GPIO.output(in1, GPIO.LOW)
            GPIO.output(in2, GPIO.LOW)
            safety_active = False
        
        time.sleep(0.5)  # Add a small delay to avoid excessive CPU usage

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
                    global sensor_enabled
                    sensor_enabled = False  # Disable sensor readings

                    # Close the webview window
                    if window:
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

window = None

def start_webview():
    global window
    window = webview.create_window('LUIGI', '/home/pi/Desktop/Luigi/Source/drive.html', width=480, height=320)
    webview.start()

if __name__ == "__main__":
    # Send initial message to ESP32
    sock.send('Hello ESP32'.encode())

    # Start double tap detection in a separate thread
    tap_thread = threading.Thread(target=detect_double_tap)
    tap_thread.start()

    # Start the UDP loop in a separate thread
    udp_thread = threading.Thread(target=udp_loop)
    udp_thread.start()

    # Start ultrasonic monitor in a separate thread
    ultrasonic_thread = threading.Thread(target=ultrasonic_monitor)
    ultrasonic_thread.start()

    # Start the webview in the main thread
    start_webview()
