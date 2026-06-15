import os
import sqlite3
import random
import smtplib
import string
from Bank_account import BANK_EMAIL, BANK_EMAIL_PASSWORD
def greet():
    print("==============================================================")
    msg = "Welcome to JH Bank"
    print(f"\t \t \t{msg}")
    return
def ask():
    msg = "what do you wish to do?"
    opt1 = "1: Register to join our bank "
    opt2 = "2. Sign-in your account"
    print(f"{msg}\n")
    print(f"{opt1}\n")
    print(f"{opt2}\n")
    return 
def error_capture_1():
    print("Invalid command please try again")
    return
##################################
#registration validation
class Register_Identity():
    @staticmethod
    def _generate_account_id():
        # Build a fresh 15-digit account number for each customer.
        digits = [d for d in range(1, 10)]
        full_number = random.sample(digits, 9) + random.sample(digits, 6)
        return int("".join(str(p) for p in full_number))

    def __init__(self,name,age,gender,status,town,phone,email,password):
        self.name = name
        self.age = age
        self.gender = gender
        self.status = status
        self.town = town
        self.phone = phone
        self.email = email
        self.password = password
        self.account_id = Register_Identity._generate_account_id()
        
    def register_not(self):
        con = sqlite3.connect("Bank_JH.db")
        cursor = con.cursor()
        cursor.execute('''
                       CREATE TABLE Customer_services(
                       Customer_Name TEXT NOT NULL,Customer_Age TEXT NOT NULL,Customer_Gender TEXT NOT NULL,Customer_Status TEXT NOT NULL,Customer_Location TEXT NOT NULL ,Customer_Phone TEXT NOT NULL ,Customer_Email TEXT NOT NULL UNIQUE PRIMARY KEY,Customer_password TEXT NOT NULL,Customer_ID INT NOT NULL
                       )''')
        cursor.execute('''
                       INSERT INTO Customer_services(Customer_Name,Customer_Age,Customer_Gender,Customer_Status ,Customer_Location ,Customer_Phone,Customer_Email,Customer_password,Customer_ID) VALUES(?,?,?,?,?,?,?,?,?)''',(self.name,self.age,self.gender,self.status,self.town,self.phone,self.email,self.password,self.account_id))
        con.commit()
        con.execute('''
                    CREATE TABLE Account(
                    Account_id,Customer_ID,Current_amount,Transaction_Date,Transaction_ID
                    )
                    ''',)
        con.commit()
        con.close()
        report = open("Bank_JH.txt","a")
        report.write(f"{self.name} \n {self.age}\n {self.gender}\n {self.status}\n {self.town} \n {self.phone} \n {self.email} \n {self.password}\n {self.account_id} \n")
        report.close()
        print("Registration successful")


    def register(self):
        con = sqlite3.connect("Bank_JH.db")
        cursor = con.cursor()
        cursor.execute('''
                       INSERT INTO Customer_services(Customer_Name,Customer_Age,Customer_Gender,Customer_Status,Customer_Location,Customer_Phone,Customer_Email,Customer_password,Customer_ID) VALUES(?,?,?,?,?,?,?,?,?)
                       ''',(self.name,self.age,self.gender,self.status,self.town,self.phone,self.email,self.password,self.account_id))
        con.execute('''
                    CREATE TABLE IF NOT EXISTS Account(
                    Account_id,Customer_ID,Current_amount,Transaction_Date,Transaction_ID
                    )
                    ''',)
        # Create the customer's account with a starting balance.
        starting_balance = 0.0   # change this if you want new accounts to start with funds
        cursor.execute('''
                       INSERT INTO Account(Account_id,Customer_ID,Current_amount,Transaction_Date,Transaction_ID)
                       VALUES(?,?,?,?,?)
                       ''',(str(self.account_id), self.account_id, starting_balance, None, None))
        con.commit()
        con.close()
        print("Registration successful")
        report = open("Bank_JH.txt","a")
        report.write(f"{self.name} \n {self.age}\n {self.gender}\n {self.status}\n {self.town} \n {self.phone} \n {self.email} \n {self.password} \n {self.account_id}\n")
        report.close()
        return


def check(name:str,password:str):
        con = sqlite3.connect("Bank_JH.db")
        cursor = con.cursor()
        cursor.execute('''
                       SELECT (Customer_password) FROM Customer_services WHERE Customer_Email = ? ''',(name,))
        data = cursor.fetchone()
        if (data != None) and (password == data[0]):
            return True###we will return the account details that is moving into the user account
        else:
            return False
#    con = sqlite3.connect("Bank_JH.db")
#    cursor = con.cursor()
#    cursor.execute("SELECT * FROM Customer_services")
#    data = cursor.fetchall()
#    for d in data:
#        if name == d[6] and pin == d[7]:
#            print("Sign-in successful")
#            return
#        print("Invalid credentials please try again")


class Sign_up_check():
    def __init__(self,name,password):
        self.name = name
        self.password = password
    
    def check(self):
        con = sqlite3.connect("Bank_JH.db")
        cursor = con.cursor()
        cursor.execute("SELECT Customer_Email, Customer_password FROM Customer_services WHERE Customer_Email = ? ",(self.name,))
        data = cursor.fetchone()
        if (data != None) and (self.name == data[0] and self.password == data[1]):
            print("You already have an account please Sign-in")
            return True
        return False
class send_email():
    def __init__(self, email, name="", password=""):
        self.email = email
        self.bank_email = BANK_EMAIL
        self.bank_password = BANK_EMAIL_PASSWORD
        self.msg = f"Thank you for signing up \nHere are your credentials\n Name is {name} \n Password is {password} \n"

    def send(self):
        smtObject = smtplib.SMTP("smtp.gmail.com", 587)
        smtObject.ehlo()
        smtObject.starttls()
        smtObject.login(self.bank_email, self.bank_password)
        smtObject.sendmail(self.bank_email, self.email, self.msg)
        smtObject.quit()
class Passwordgenerator():
    def __init__(self):
        self.password = ""

    @staticmethod
    def generate():
        words = string.ascii_lowercase
        WORDs = string.ascii_uppercase
        num = "1234567890"
        sym = "!£$%^&*()_+}{?/"
        WRDs = random.sample(WORDs,k=3)
        wrd = random.sample(words,k=3)
        nums = random.sample(num,k=2)
        syms = random.sample(sym,k=2)
        sometxt = WRDs+wrd+syms+nums
        random.shuffle(sometxt)
        password = "".join(sometxt)
        return password
        



