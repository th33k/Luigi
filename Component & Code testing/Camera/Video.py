import time
import picamera

with picamera.PiCamera() as camera:
    camera.resolution = (1280, 720)  # Set the resolution
    camera.start_preview()           # Start the preview
    camera.start_recording('video.h264')  # Start recording
    time.sleep(10)                   # Record for 10 seconds
    camera.stop_recording()          # Stop recording
