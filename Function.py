import tkinter as tk
import subprocess
import random
import smbus
import time
import threading
import pygame

# MPU6050 Registers
MPU6050_ADDR = 0x68
PWR_MGMT_1 = 0x6B
ACCEL_XOUT_H = 0x3B
ACCEL_YOUT_H = 0x3D
ACCEL_ZOUT_H = 0x3F

# Initialize pygame mixer
pygame.mixer.init()
shake_sound = pygame.mixer.Sound('/home/pi/Desktop/Luigi/Source/Audio/blink.wav')  # Path to your sound file

# Function to initialize MPU6050
def init_mpu6050():
    bus = smbus.SMBus(1)
    bus.write_byte_data(MPU6050_ADDR, PWR_MGMT_1, 0)

# Function to read a word from MPU6050
def read_word(bus, addr, reg):
    high = bus.read_byte_data(addr, reg)
    low = bus.read_byte_data(addr, reg + 1)
    val = (high << 8) + low
    if val >= 0x8000:
        return -((65535 - val) + 1)
    else:
        return val

# Function to detect shake
def detect_shake(bus):
    threshold = 20000
    accel_x = read_word(bus, MPU6050_ADDR, ACCEL_XOUT_H)
    accel_y = read_word(bus, MPU6050_ADDR, ACCEL_YOUT_H)
    accel_z = read_word(bus, MPU6050_ADDR, ACCEL_ZOUT_H)
    return abs(accel_x) > threshold or abs(accel_y) > threshold or abs(accel_z) > threshold

# Function to open a Python file or exit application
def open_python_file(file):
    global running
    running = False
    subprocess.Popen(['python3', file])
    root.destroy()  # Exit the application

# Hover effect functions for the buttons
def on_enter_button(event):
    event.widget.config(bg="white", fg="black")

def on_leave_button(event):
    event.widget.config(bg="purple1", fg="white")

# Hover effect functions for the central button
def on_enter(event):
    canvas.itemconfig(circle, fill="midnightblue")

def on_leave(event):
    canvas.itemconfig(circle, fill="purple1")

# Create the main window
root = tk.Tk()
root.title("Python File Launcher")
root.attributes("-fullscreen", True)  # Set fullscreen mode
root.geometry("1024x768")
root.configure(bg="black")

button_font = ("Helvetica", 22, "bold")
button_font2 = ("Helvetica", 48,"bold")

# Create buttons for the left side
left_button1 = tk.Button(root, text="Click Bubble",font=button_font, command=lambda: open_python_file('/home/pi/Desktop/Luigi/Functions/Games/Click Bubble.py'), bg="purple1", fg="white")
left_button1.place(x=40, y=130, width=200, height=100)
left_button1.bind("<Enter>", on_enter_button)
left_button1.bind("<Leave>", on_leave_button)

left_button2 = tk.Button(root, text="Mind Puzzle",font=button_font, command=lambda: open_python_file('/home/pi/Desktop/Luigi/Functions/Games/Mind Puzzle.py'), bg="purple1", fg="white")
left_button2.place(x=40, y=270, width=200, height=100)
left_button2.bind("<Enter>", on_enter_button)
left_button2.bind("<Leave>", on_leave_button)

left_button3 = tk.Button(root, text="✊ ✋ ✌", font=button_font2, command=lambda: open_python_file('/home/pi/Desktop/Luigi/Functions/Games/RPS/RPS.py'), bg="purple1", fg="white")
left_button3.place(x=40, y=410, width=200, height=100)
left_button3.bind("<Enter>", on_enter_button)
left_button3.bind("<Leave>", on_leave_button)

left_button4 = tk.Button(root, text="Selfie",font=button_font, command=lambda: open_python_file('/home/pi/Desktop/Luigi/Functions/Selfie/selfie.py'), bg="purple1", fg="white")
left_button4.place(x=40, y=550, width=200, height=100)
left_button4.bind("<Enter>", on_enter_button)
left_button4.bind("<Leave>", on_leave_button)

# Create buttons for the right side
right_button1 = tk.Button(root, text="Clock",font=button_font, command=lambda: open_python_file('/home/pi/Desktop/Luigi/Source/digitalclock.py'), bg="purple1", fg="white")
right_button1.place(x=784, y=130, width=200, height=100)
right_button1.bind("<Enter>", on_enter_button)
right_button1.bind("<Leave>", on_leave_button)

right_button2 = tk.Button(root, text="Hey LUIGI",font=button_font, command=lambda: open_python_file('/home/pi/Desktop/Luigi/Functions/Hey_Luigi/Hey_Luigi.py'), bg="purple1", fg="white")
right_button2.place(x=784, y=270, width=200, height=100)
right_button2.bind("<Enter>", on_enter_button)
right_button2.bind("<Leave>", on_leave_button)

right_button3 = tk.Button(root, text="Drive",font=button_font, command=lambda: open_python_file('/home/pi/Desktop/Luigi/Remote_Control/Bluetooth.py'), bg="purple1", fg="white")
right_button3.place(x=784, y=410, width=200, height=100)
right_button3.bind("<Enter>", on_enter_button)
right_button3.bind("<Leave>", on_leave_button)

right_button4 = tk.Button(root, text="Sleep",font=button_font, command=lambda: open_python_file('/home/pi/Desktop/Luigi/Source/Sleep.py'), bg="purple1", fg="white")
right_button4.place(x=784, y=550, width=200, height=100)
right_button4.bind("<Enter>", on_enter_button)
right_button4.bind("<Leave>", on_leave_button)

# Create the central round button using Canvas
canvas = tk.Canvas(root, width=300, height=300, highlightthickness=0, bg="black")
canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# Draw a larger circle on the canvas with a thicker border
circle = canvas.create_oval(0, 0, 300, 300, fill="purple1", outline="black", width=8)

# Add text to the circle to make it look like a button
text = canvas.create_text(150, 150, text="GO BACK", justify=tk.CENTER, font=("Helvetica", 24, "bold"), fill="white")

# Bind click event to the canvas
canvas.tag_bind(circle, "<Button-1>", lambda event: open_python_file('/home/pi/Desktop/Luigi/Home.py'))
canvas.tag_bind(text, "<Button-1>", lambda event: open_python_file('/home/pi/Desktop/Luigi/Home.py'))

# Bind hover effects to the circle and text
canvas.tag_bind(circle, "<Enter>", on_enter)
canvas.tag_bind(circle, "<Leave>", on_leave)
canvas.tag_bind(text, "<Enter>", on_enter)
canvas.tag_bind(text, "<Leave>", on_leave)

# Function to change button colors randomly
def change_button_colors():
    colors = ["darkred", "darkblue", "darkgreen", "darkorange", "purple", "teal", "navy", "maroon"]
    random_color = random.choice(colors)
    buttons = [left_button1, left_button2, left_button3, left_button4, right_button1, right_button2, right_button3, right_button4]
    for button in buttons:
        button.config(bg=random_color)
    canvas.itemconfig(circle, fill=random_color)

# Function to check for shakes and change button colors
def check_for_shakes():
    bus = smbus.SMBus(1)
    init_mpu6050()
    shake_count = 0
    while running:
        if detect_shake(bus):
            shake_count += 1
            if shake_count == 3:
                shake_count = 0
                change_button_colors()
                shake_sound.play()
        time.sleep(0.1)

# Start shake detection in a separate thread
running = True
shake_thread = threading.Thread(target=check_for_shakes)
shake_thread.daemon = True
shake_thread.start()

# Run the application
root.mainloop()
