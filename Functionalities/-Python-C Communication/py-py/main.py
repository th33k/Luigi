user_input = input("Enter 1, 2, or anything else: ")

if user_input == '1':
    import pro1
elif user_input == '2':
    import pro2
else:
    print("Welcome to the user information program!")
    print("Please provide your details:")
    
    # Gather user input
    name = input("Enter your name: ")
    age = input("Enter your age: ")
    phone_number = input("Enter your phone number: ")

    import pro3
    # Pass input values to pro3.py
    name, age, phone_number = pro3.get_user_info(name, age, phone_number)

    print("\nUser Information:")
    print("Name:", name)
    print("Age:", age)
    print("Phone Number:", phone_number)
