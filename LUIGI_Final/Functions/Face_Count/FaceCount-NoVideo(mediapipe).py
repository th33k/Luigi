import cv2
import time
import mediapipe as mp

def detect_faces():
    # Initialize MediaPipe Face Detection
    mp_face_detection = mp.solutions.face_detection
    face_detection = mp_face_detection.FaceDetection(min_detection_confidence=0.5)

    # Start video capture from the webcam
    cap = cv2.VideoCapture(0)

    if not cap.isOpened():
        print("Error: Unable to access the webcam.")
        return

    last_capture_time = time.time()

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if not ret:
            print("Error: Unable to read from the webcam.")
            break

        current_time = time.time()

        # Capture and process frame every second
        if current_time - last_capture_time >= 1:
            # Update last capture time
            last_capture_time = current_time

            # Convert the frame to RGB
            rgb_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

            # Perform face detection
            results = face_detection.process(rgb_frame)

            # Print the number of detected faces
            if results.detections:
                print(f"Number of faces detected: {len(results.detections)}")
            else:
                print("Number of faces detected: 0")

        # Break the loop if 'q' key is pressed
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    # Release the video capture object
    cap.release()

# Run the face detection
detect_faces()
