import Bank_bulid_1 as start
from Bank_bulid_1 import Register_Identity 
from Bank_bulid_1 import Sign_up_check
import os
import time
import random
import re
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
        password = input("Enter your password: ")
        const = len(password) == 4 and password.isdigit()
        while not const:
            print("Invalid Pin!")
            password = input("Enter your password: ")
            const = len(password) == 4 and password.isdigit()
        if os.path.exists("Bank_JH.db"):
            start.check(username,password)
        else:
            print("No account found please register to create an account")
    elif int(user) == 1:
        print("Wait while we Register you")
        time.sleep(5)
        while True:
            username = input("Enter your full name (seperated with a space): ")
            name_verify =re.compile(r"([a-zA-Z]{3,8})",re.VERBOSE)
            #+\s+[a-zA-Z]+\s[a-zA-Z]+[a-zA-Z]+\s)",re.VERBOSE)
            #name_check = name_verify(username)
            name_split = username.split(" ")
            c = 0
            for n in name_split:
                in_check = name_verify.match(n)
                if in_check != None :
                    c +=1
                else:
                    pass
            if c != len(name_split):
                print("Invalid name! Username should be only alphabets!! and should not contain space at the end")
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
            Tele = input("Enter your Contact 050-000-0000: ")
            check_phonenumber = re.compile(r"\d\d\d-\d\d\d-\d\d\d\d")
            checker = check_phonenumber.match(Tele)
            if checker != None :
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
            regexp = re.compile(r'''([a-zA-Z0-9._%+-]+@+[a-zA-Z0-9.-]+(\.[a-zA-Z]{2,4}))''',re.VERBOSE)
            check_email = regexp.match(email)
            if check_email != None :
            #if "@" in email and "." in email and email.endswith(".com"):
                break
            else:
                print("Invalid Email! email must contain '@' and '.'")
        time.sleep(5)
        while True:
            password = input("Enter a new password: ")
            const = len(password) == 4 and password.isdigit()
            if const:
                break
            else:
                print("Invalid Pin! password must be a 4-digit number")
        stat = ("Single","Married","Student")
        time.sleep(5)
        while True:
            status = input("Enter your status: (Single/Married/Student): ")
            if status in stat:
                break
            else:
                print("Invalid Status!")
        verify = re.compile(r"[a-zA-Z0-9.!£$%^&*()_+|]{8,20}")
        while True:
            password = input("Enter password: ")
            check = verify.match(password)
            if check != None:
                break
            else:
                print("Create a Strong password")
        while True:
            print("confirm password")
            confirm = input("Enter Password again!")
            if confirm == password:
                break
            else:
                print("Password doesn't match")
        if os.path.exists("Bank_JH.db"):
            check_first = Sign_up_check(email,password)
            if check_first.check():
                print("You already have an account please Sign-in")
            else:
                customer = start.Register_Identity(name,age,gender,status,location,Tele,email,password)
                customer.register()
                print("Account created successfully")
                print("Please Sign-in to continue")
        else:
            customer = start.Register_Identity(name,age,gender,status,location,Tele,email,password)
            customer.register_not()
            print(f"Please sign-in to continue")
            print("Account created successfully")
    elif int(user) == 0:
        print("Thank You for choosing us")
    else:
        start.error_capture_1()


