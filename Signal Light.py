from gpiozero import AngularServo
from time import sleep

# Define servo with appropriate pin and pulse width range
servo = AngularServo(21, min_angle=-90, max_angle=90)

try:
    while True:
        # Rotate servo to the left (angle = -90) for 0.5 second
        servo.angle = -90
        sleep(0.3)
        
        # Rotate servo to the center (angle = 0) for 1 second
        servo.angle = 0
        sleep(0.5)
        
        # Rotate servo to the right (angle = 90) for 0.5 second
        servo.angle = 90
        sleep(0.3)

except KeyboardInterrupt:
    # Cleanup GPIO on keyboard interrupt
    servo.close()
