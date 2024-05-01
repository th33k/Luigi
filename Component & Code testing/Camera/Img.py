import time
import picamera

with picamera.PiCamera() as camera:
    camera.resolution = (1280, 720)  # Set the resolution
    camera.start_preview()           # Start the preview
    time.sleep(2)                    # Allow the camera to adjust
    camera.capture('image.jpg')      # Capture an image and save it
