import os
import sqlite3
import random
import smtplib
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
    x = [x for x in range(1,10)]
    counter = random.sample(x,9)
    enter = random.sample(x,6)
    c = str()
    v = str()
    for p in counter:
        c+=str(p)
    for n in enter:
        v += str(n)
    c = str(c)+str(n)
    c =int(c)
    def __init__(self,name,age,gender,status,town,phone,email,password):
        self.name = name
        self.age = age
        self.gender = gender
        self.status = status
        self.town = town
        self.phone = phone
        self.email = email
        self.password = password
        self.account_id = Register_Identity.c
        
    def register_not(self):
        con = sqlite3.connect("Bank_JH.db")
        cursor = con.cursor()
        cursor.execute("CREATE TABLE Customer_services(Customer_Name TEXT NOT NULL,Customer_Age TEXT NOT NULL,Customer_Gender TEXT NOT NULL,Customer_Status TEXT NOT NULL,Customer_Location TEXT NOT NULL ,Customer_Phone TEXT NOT NULL ,Customer_Email TEXT NOT NULL UNIQUE PRIMARY KEY,Customer_password NOT NULL TEXT NOT NULL,Customer_ID INT NOT NULL)")
        cursor.execute("INSERT INTO Customer_services(Customer_Name,Customer_Age,Customer_Gender,Customer_Status ,Customer_Location ,Customer_Phone,Customer_Email,Customer_password,Customer_ID) VALUES(?,?,?,?,?,?,?,?,?)",(self.name,self.age,self.gender,self.status,self.town,self.phone,self.email,self.password,self.account_id))
        con.commit()
        con.close()
        report = open("Bank_JH.txt","a")
        report.write(f"{self.name} \n {self.age}\n {self.gender}\n {self.status}\n {self.town} \n {self.phone} \n {self.email} \n {self.password}\n {self.account_id} \n")
        report.close()
        print("Registration successful")


    def register(self):
        con = sqlite3.connect("Bank_JH.db")
        cursor = con.cursor()
        cursor.execute("INSERT INTO Customer_services(Customer_Name,Customer_Age,Customer_Gender,Customer_Status ,Customer_Location ,Customer_Phone,Customer_Email,Customer_password NOT NULL,Customer_ID) VALUES(?,?,?,?,?,?,?,?,?)",(self.name,self.age,self.gender,self.status,self.town,self.phone,self.email,self.password,self.account_id))
        con.commit()
        con.close()
        print("Registration successful")
        report = open("Bank_JH.txt","w+")
        report.write(f"{self.counter}")
        report.write(f"{self.name} \n {self.age}\n {self.gender}\n {self.status}\n {self.town} \n {self.phone} \n {self.email} \n {self.password} \n {self.account_id}\n")
        report.close()
        return


def check(name,password):
        con = sqlite3.connect("Bank_JH.db")
        cursor = con.cursor()
        cursor.execute("SELECT (Customer_Email,Customer_password) FROM Customer_service WHERE Customer_Email = ? ",(name,))
        data = cursor.fetchone()
        if (data != None) and (name == data[0] and password == data[1]):
            print("Sign-in successful")
            return
        print("Invalid credentials please try again")
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
        cursor.execute("SELECT (Customer_Email,Customer_password) FROM Customer_service WHERE Customer_Email = ? ",(self.name,))
        data = cursor.fetchone()
        if (data != None) and (self.name == data[0] and self.password == data[1]):
            print("You already have an account please Sign-in")
            return True
        return False
class send_email():
    def __init__(self,email):
        self.email = email
        self.bank_email = "customizedemail@gmail.com"
    
    def send(self):
        smtObject = smtplib.SMTP("smtp.gmail.com",587)
        smtObject.ehlo()
        smtObject.starttls()    
        smtObject.login(self.bank_email,"password")
        smtObject.sendmail(self.bank_email, self.email, "Subject: Welcome to our bank!\n\nThank you for signing up.")



