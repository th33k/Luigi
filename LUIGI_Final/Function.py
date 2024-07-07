import tkinter as tk
import subprocess

# Function to open a Python file or exit application
def open_python_file(file):
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
root.attributes("-fullscreen", False)  # Set fullscreen mode
root.geometry("1024x768")
root.configure(bg="black")

button_font = ("Helvetica", 40, "bold")

# Create buttons for the left side
left_button1 = tk.Button(root, text="Click Bubble", command=lambda: open_python_file('/home/pi/Desktop/LUIGI_Final/Functions/Games/Click_Bubble.py'), bg="purple1", fg="white")
left_button1.place(x=40, y=130, width=200, height=100)
left_button1.bind("<Enter>", on_enter_button)
left_button1.bind("<Leave>", on_leave_button)

left_button2 = tk.Button(root, text="Mind Puzzle", command=lambda: open_python_file('/home/pi/Desktop/LUIGI_Final/Functions/Games/Mind_Puzzle.py'), bg="purple1", fg="white")
left_button2.place(x=40, y=270, width=200, height=100)
left_button2.bind("<Enter>", on_enter_button)
left_button2.bind("<Leave>", on_leave_button)

left_button3 = tk.Button(root, text="✊✋✌", font=button_font, command=lambda: open_python_file('/home/pi/Desktop/LUIGI_Final/Functions/Games/RPS/RPS.py'), bg="purple1", fg="white")
left_button3.place(x=40, y=410, width=200, height=100)
left_button3.bind("<Enter>", on_enter_button)
left_button3.bind("<Leave>", on_leave_button)

left_button4 = tk.Button(root, text="Hey LUIGI", command=lambda: open_python_file('/home/pi/Desktop/LUIGI_Final/Functions/Hey_Luigi/Hey_luigi.py'), bg="purple1", fg="white")
left_button4.place(x=40, y=550, width=200, height=100)
left_button4.bind("<Enter>", on_enter_button)
left_button4.bind("<Leave>", on_leave_button)

# Create buttons for the right side
right_button1 = tk.Button(root, text="Clock", command=lambda: open_python_file('/home/pi/Desktop/LUIGI_Final/HTML/clock.py'), bg="purple1", fg="white")
right_button1.place(x=784, y=130, width=200, height=100)
right_button1.bind("<Enter>", on_enter_button)
right_button1.bind("<Leave>", on_leave_button)

right_button2 = tk.Button(root, text="Selfie", command=lambda: open_python_file('/home/pi/Desktop/LUIGI_Final/Functions/Selfie/Selfie.py'), bg="purple1", fg="white")
right_button2.place(x=784, y=270, width=200, height=100)
right_button2.bind("<Enter>", on_enter_button)
right_button2.bind("<Leave>", on_leave_button)

right_button3 = tk.Button(root, text="Drive", command=lambda: open_python_file('/home/pi/Desktop/LUIGI_Final/Remote Control/UDPControl(Testing).py'), bg="purple1", fg="white")
right_button3.place(x=784, y=410, width=200, height=100)
right_button3.bind("<Enter>", on_enter_button)
right_button3.bind("<Leave>", on_leave_button)

right_button4 = tk.Button(root, text="Sleep", command=lambda: open_python_file('/home/pi/Desktop/LUIGI_Final/HTML/sleep.py'), bg="purple1", fg="white")
right_button4.place(x=784, y=550, width=200, height=100)
right_button4.bind("<Enter>", on_enter_button)
right_button4.bind("<Leave>", on_leave_button)

# Create the central round button using Canvas
canvas = tk.Canvas(root, width=300, height=300, highlightthickness=0, bg="black")
canvas.place(relx=0.5, rely=0.5, anchor=tk.CENTER)

# Draw a larger circle on the canvas with a thicker border
circle = canvas.create_oval(0, 0, 300, 300, fill="purple1", outline="black", width=8)

# Add text to the circle to make it look like a button
text = canvas.create_text(150, 150, text="Go Back", justify=tk.CENTER, font=("Helvetica", 24, "bold"), fill="white")

# Bind click event to the canvas
canvas.tag_bind(circle, "<Button-1>", lambda event: open_python_file('/home/pi/Desktop/LUIGI_Final/Home.py'))
canvas.tag_bind(text, "<Button-1>", lambda event: open_python_file('/home/pi/Desktop/LUIGI_Final/Home.py'))

# Bind hover effects to the circle and text
canvas.tag_bind(circle, "<Enter>", on_enter)
canvas.tag_bind(circle, "<Leave>", on_leave)
canvas.tag_bind(text, "<Enter>", on_enter)
canvas.tag_bind(text, "<Leave>", on_leave)

# Run the application
root.mainloop()
