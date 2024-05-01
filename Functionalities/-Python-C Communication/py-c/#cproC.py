import ctypes
import subprocess
import os

# Change working directory to where the script resides
os.chdir(r"C:\Users\theek\OneDrive - University of Moratuwa\!Obsidian\Desktop pi\#Log\C Python\int")  # Replace this with the actual directory path

# Compile C programs
subprocess.run(['gcc', '-shared', '-o', 'c_program1.so', '-fPIC', 'c_program1.c'])
subprocess.run(['gcc', '-shared', '-o', 'c_program2.so', '-fPIC', 'c_program2.c'])

# Load the C libraries
c_program1 = ctypes.CDLL('./c_program1.so')
c_program2 = ctypes.CDLL('./c_program2.so')

# Define the return type of the function
c_program1.get_input_from_user.restype = ctypes.c_int

# Call the C function to get input from the user
input_value = c_program1.get_input_from_user()

# Add 12 to the input value
result = input_value + 12

# Call another C program (c_program2) with the result
c_program2.print_value_from_python.argtypes = [ctypes.c_int]
c_program2.print_value_from_python(result)
