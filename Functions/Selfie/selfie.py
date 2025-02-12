import cv2
import os
import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk
from datetime import datetime
import RPi.GPIO as GPIO
import subprocess
import time
import threading
import sys

# Directory to save photos
save_dir = "img"
os.makedirs(save_dir, exist_ok=True)

# Initialize the camera
cap = cv2.VideoCapture(0)

# Create the main window
root = tk.Tk()
root.title("Selfie App")
root.attributes('-fullscreen', True)  # Fullscreen

# Create a frame for the camera and controls
camera_frame = tk.Frame(root)
camera_frame.grid(row=0, column=0, sticky="nsew")

# Create a label to display the camera feed
camera_label = tk.Label(camera_frame)
camera_label.pack(expand=True, fill=tk.BOTH)

# Create a frame for the gallery
gallery_frame = tk.Frame(root)
gallery_frame.grid(row=1, column=0, pady=20, sticky="nsew")

# Configure row and column weights for the main window
root.grid_rowconfigure(0, weight=3)  # Give more weight to the camera row
root.grid_rowconfigure(1, weight=1)  # Less weight to the gallery row
root.grid_columnconfigure(0, weight=1)

# Variables to store the captured image and gallery pagination
captured_image = None
current_page = 0
photos_per_page = 5

button_font = ("Helvetica", 15, "bold")

# Function to update the camera feed
def update_camera_feed():
    global captured_image
    if captured_image is None:
        ret, frame = cap.read()
        if ret:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            img = Image.fromarray(frame)
            imgtk = ImageTk.PhotoImage(image=img)
            camera_label.imgtk = imgtk
            camera_label.configure(image=imgtk)
    camera_label.after(10, update_camera_feed)

# Function to capture the image
def capture_image():
    global captured_image
    ret, frame = cap.read()
    if ret:
        captured_image = frame
        img = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        imgtk = ImageTk.PhotoImage(image=img)
        camera_label.imgtk = imgtk
        camera_label.configure(image=imgtk)
        capture_button.pack_forget()
        save_button.pack(side=tk.LEFT, padx=10)
        try_again_button.pack(side=tk.RIGHT, padx=10)
        save_button.config(state=tk.NORMAL)
        try_again_button.config(state=tk.NORMAL)

# Function to save the image with date and time
def save_image():
    global captured_image
    if captured_image is not None:
        filename = os.path.join(save_dir, f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg")
        cv2.imwrite(filename, captured_image)
        messagebox.showinfo("Image Saved", "Your image has been saved!")
        save_button.pack_forget()
        try_again_button.pack_forget()
        capture_button.pack(pady=10)
        captured_image = None
        load_gallery()

# Function to try capturing again
def try_again():
    global captured_image
    captured_image = None
    save_button.pack_forget()
    try_again_button.pack_forget()
    capture_button.pack(pady=10)
    save_button.config(state=tk.DISABLED)
    try_again_button.config(state=tk.DISABLED)

# Function to delete an image
def delete_image(image_path, image_label, delete_button):
    if messagebox.askyesno("Delete Image", "Are you sure you want to delete this image?"):
        os.remove(image_path)
        image_label.destroy()
        delete_button.destroy()
        load_gallery()

# Function to view the image in full size with close button
def view_image(image_path):
    view_window = tk.Toplevel(root)
    view_window.title("View Image")
    view_window.attributes('-fullscreen', True)  # Fullscreen
    img = Image.open(image_path)
    img = ImageTk.PhotoImage(img)
    img_label = tk.Label(view_window, image=img)
    img_label.image = img
    img_label.pack(expand=True, fill=tk.BOTH)
    close_button = tk.Button(view_window, text="Close", font=button_font, width=20, height=3, command=view_window.destroy)
    close_button.pack(pady=20)

# Function to create the delete button
def create_delete_button(photo, img_label, row, column):
    delete_button = tk.Button(gallery_frame, text="Delete", command=lambda: delete_image(photo, img_label, delete_button))
    delete_button.grid(row=row, column=column, padx=5, pady=5)
    return delete_button

# Function to load the gallery
def load_gallery():
    for widget in gallery_frame.winfo_children():
        widget.destroy()
    photos = [os.path.join(save_dir, f) for f in os.listdir(save_dir) if f.endswith('.jpg')]
    start_index = current_page * photos_per_page
    end_index = start_index + photos_per_page
    for i, photo in enumerate(photos[start_index:end_index]):
        img = Image.open(photo)
        img.thumbnail((100, 100))
        img = ImageTk.PhotoImage(img)
        img_label = tk.Label(gallery_frame, image=img)
        img_label.image = img
        img_label.grid(row=0, column=i * 2, padx=5, pady=5)
        img_label.bind("<Button-1>", lambda e, p=photo: view_image(p))

        create_delete_button(photo, img_label, 0, i * 2 + 1)

    # Navigation buttons
    if current_page > 0:
        prev_button = tk.Button(gallery_frame, text="Previous", font=button_font, width=12, height=2, command=lambda: change_page(-1))
        prev_button.grid(row=1, column=0, padx=1, pady=5)
    if end_index < len(photos):
        next_button = tk.Button(gallery_frame, text="Next", font=button_font, width=12, height=2, command=lambda: change_page(1))
        next_button.grid(row=1, column=photos_per_page * 2 - 1, padx=1, pady=5)

# Function to change the gallery page
def change_page(direction):
    global current_page
    current_page += direction
    load_gallery()

# Capture button
capture_button = tk.Button(camera_frame, text="Capture Image", font=button_font, command=capture_image, width=25, height=3)
capture_button.pack(pady=10)

# Save button
save_button = tk.Button(camera_frame, text="Save Image", font=button_font, command=save_image, state=tk.DISABLED, width=25, height=3)
save_button.pack_forget()

# Try again button
try_again_button = tk.Button(camera_frame, text="Try Again", font=button_font, command=try_again, state=tk.DISABLED, width=25, height=3)
try_again_button.pack_forget()

# GPIO and double-tap detection setup
TOUCH_PIN = 5  # GPIO pin connected to the touch sensor

# Setup GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setup(TOUCH_PIN, GPIO.IN)

# Time interval for detecting double tap (in seconds)
DOUBLE_TAP_INTERVAL = 0.5

# Variables to keep track of taps and sensor state
last_tap_time = 0
tap_count = 0

def detect_double_tap():
    global last_tap_time, tap_count, root
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
                    # Close the application window
                    root.quit()  # Use quit() instead of destroy()
                    break

                # Debounce delay
                while GPIO.input(TOUCH_PIN) == GPIO.HIGH:
                    time.sleep(0.01)

            time.sleep(0.01)
    except KeyboardInterrupt:
        print("Exiting program")
    finally:
        GPIO.cleanup()
        subprocess.run(['python', '/home/pi/Desktop/Luigi/Function.py'])
        sys.exit(0)  # Exit the script

# Start the double tap detection in a separate thread
detection_thread = threading.Thread(target=detect_double_tap)
detection_thread.daemon = True  # Ensure the thread exits when the main program exits
detection_thread.start()

# Start the camera feed
update_camera_feed()

# Run the Tkinter event loop
root.mainloop()

# Release the camera
cap.release()
cv2.destroyAllWindows()
