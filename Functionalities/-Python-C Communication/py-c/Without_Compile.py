import ctypes
import os

# Set the working directory to where the script resides
script_dir = os.path.dirname(os.path.abspath(__file__))
os.chdir(script_dir)

# Load the C library
c_program1 = ctypes.CDLL('./c_program1.so')

# Define the return type of the function
c_program1.get_input_from_user.restype = ctypes.c_int

# Call the C function to get input from the user
input_value = c_program1.get_input_from_user()

# Add 12 to the input value
result = input_value + 12

# Call another C program (c_program2) with the result
c_program2 = ctypes.CDLL('./c_program2.so')
c_program2.print_value_from_python.argtypes = [ctypes.c_int]
c_program2.print_value_from_python(result)
