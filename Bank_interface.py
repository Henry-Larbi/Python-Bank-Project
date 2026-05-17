import Bank_bulid_1 as start
from Bank_bulid_1 import Register_Identity 
from Bank_bulid_1 import Sign_up_check
import os
import time
import random
#we greet the User
start.greet()
#Ask User for purpose
start.ask()
#Accept user's request
user = input("Enter option or 0 to exit from interface: ")

#we validate user's input
#we catch the user's error
try:
    int(user)
except ValueError:
    print("Command doesn't exits")
else:
    if int(user) == 2:

        print("Wait while we sign you in")
        time.sleep(5)
        while True:
            username = input("Enter your account's name: ")
            if username.isalpha():
                break
            else:
                print("Invalid Username! username can't contain spaces or numbers or special characters")
        pin = input("Enter your pin: ")
        const = len(pin) == 4 and pin.isdigit()
        while not const:
            print("Invalid Pin!")
            pin = input("Enter your pin: ")
            const = len(pin) == 4 and pin.isdigit()
        if os.path.exists("Bank_JH.db"):
            start.check(username,pin)
        else:
            print("No account found please register to create an account")
    elif int(user) == 1:
        print("Wait while we Register you")
        time.sleep(5)
        while True:   
            username = input("Enter your full name (seperated with a space): ")
            name_split = username.split(" ")
            c = 0
            x = len(name_split)
            for n in name_split:
                if n.isalpha():
                    c +=1
                else:
                    pass
            if x != c or len(name_split) < 2:
                print("Invalid name! Username should be only alphabets!! and should be more than")
            else:
                break
        msg = "wait while we generate your account username"
        print("========================================================")
        print(f"{msg}")
        time.sleep(0)
#####################################
        p = list()
        d = ""
        for m in name_split:
            p.append(m[0].lower())
            d += p.pop()
        add = name_split[0].lower()
        name = str(d+add)
        time.sleep(5)
        print(f"Your username for our bank is {name}")
        cont = Register_Identity.c
        print(f"Your account number is {cont}")
        print("Please remember your username and account number to sign-in to your account")
##########################################        
        while True:
            age = input("Enter your age: ")
            if age.isdigit() and int(age) > 0 and int(age) < 120:
                break
            else:
                print("Invalid Age! age must be a positive number")
########################################
        time.sleep(5)
        while True:
            fixed_gender = ("Male","Female")
            gender = input("Enter your gender: (Male/Female): ")
            if gender in fixed_gender:
                break
            else:
                print("Invalid gender!")
###########################################
        time.sleep(5)
        while True:
            Tele = input("Enter your Contact 0500000000: ")
            if Tele.isdigit() and len(Tele) == 10:
                break
            else:
                print("Invalid Input!")
#############################################
        time.sleep(5)
        while True:
            location = input("Enter your Location: ")
            if  location.isalpha():
                break
            else:
                print("Invalid Location! location can't contain spaces or numbers special characters")
############################################
        time.sleep(5)
        while True:
            email = input("Enter your email: ")
            if "@" in email and "." in email:
                break
            else:
                print("Invalid Email! email must contain '@' and '.'")
        time.sleep(5)
        while True:
            pin = input("Enter a new pin: ")
            const = len(pin) == 4 and pin.isdigit()
            if const:
                break
            else:
                print("Invalid Pin! pin must be a 4-digit number")
        time.sleep(5)
        while True:
            confirm_pin = input("Confirm the pin you entered: ")
            if confirm_pin == pin:
                break
            else:
                print("Pins do not match! please try again")
        stat = ("Single","Married","Student")
        time.sleep(5)
        while True:
            status = input("Enter your status: (Single/Married/Student): ")
            if status in stat:
                break
            else:
                print("Invalid Status!")
        if os.path.exists("Bank_JH.db"):
            check_first = Sign_up_check(name,pin)
            if check_first.check():
                print("You already have an account please Sign-in")
            else:
                customer = start.Register_Identity(name,age,gender,status,location,Tele,email,pin)
                customer.register()
                print("Account created successfully")
                print("Please Sign-in to continue")
        else:
            customer = start.Register_Identity(name,age,gender,status,location,Tele,email,pin)
            customer.register_not()
            print(f"Please sign-in to continue")
            print("Account created successfully")
    elif int(user) == 0:
        print("Thank You for choosing us")
    else:
        start.error_capture_1()


