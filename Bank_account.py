import sqlite3
from datetime import datetime
import time
import random as rd
class Account():
    def __init__(self, name, balance):
        self.name = name
        self.balance = balance

    def greet(self):
        print(f"Welcome Back {self.name}")
    
    def show_account_balance(self,):
        print(f"Your account balance is {self.balance}")
        

class Changepin():
    def __init__(self,name,new_pin):
        self.name = name
        self.new_pin = new_pin
        
    def change(self):
        conn  = sqlite3.connect("Bank_JH.db")
        cursor = conn.cursor()
        cursor.execute("UPDATE Customer_services SET Customer_pin = ? WHERE  Customer_Name = ?",(self.new_pin,self.name))
        conn.commit()
        conn.close()
        

class Amount():
    def __init__(self,account):
        self.amount = int()
        self.account = account
    
    def check_amount(self):
        conn = sqlite3.connect("Bank_JH.db")
        cur = conn.cursor()
        cur.execute("SELECT * FROM Account where Account_id = ?",(self.account))
        amount = cur.fetchone()
        conn.commit()
        conn.close()
        current = amount[0]
        return current 
    


class Transaction():
    def __init__(self,receiver,amount,account,name):
        self.receiver = receiver
        self.amount = amount
        self.transaction_id = int()
        self.account_id = account
        self.name = name

    def check(self):
        conn = sqlite3.connect("Bank_JH.db")
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM Account where Account_id = ?",(self.account_id))
        #cursor.execute("SELECT  FROM  Account INNER JOIN Customer_services ON Account.Account_id = Customer_services.Customer_ID  WHERE Customer_services.Customer_Name= ?",(self.name))
        amount = cursor.fetchone()
        conn.commit()
        conn.close()
        current = amount[0]
        if current >= self.amount:
            return True
        else:
            print("Insufficient Amount Please Recharge!!")
            return False
        


        #cursor.execute("SELECT Current_ammount FROM Account WHERE ")
    def send(self,confirm):
        if confirm:
            conn = sqlite3.connect("Bank_JH.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE Account SET Current_amount = Current_amount-?",(self.amount))
            conn.commit()
            conn.close()
            print("Transaction was successfull!")


    def transaction_generator(self):
        transac_1 = rd.sample(range(1, 10), 9)
        rd.shuffle(transac_1)
        id_initial = str()
        for c in transac_1:
            id_initial += str(c)
        self.transaction_id = int(id_initial)
  

    def transaction_report(self):
        transaction_day = datetime.today()
        transaction_time = time.strftime("%H:%M:%S")
        with open("Bank_Transaction.txt", "w+") as transact:
            transact.write("Transaction Initiated\n")
            transact.write(f"User {self.receiver} received GHc{self.amount:.2f} at {transaction_time}, {transaction_day}\n")
            transact.write("Transaction Successful \n")

    def transaction_record(self):
        transaction_day = datetime.today()
        conn = sqlite3.connect("Bank_JH.db")
        cur = conn.cursor()
        cur.execute("UPDATE Account SET Transaction_ID = ? WHERE Account_id = ?", (self.transaction_id, self.account_id))
        cur.execute("UPDATE Account SET Transaction_Date = ? WHERE Account_id = ?", (transaction_day, self.account_id))
        conn.commit()
        conn.close()
    
    def report_csv(self):
        """Generate CSV report of transactions"""
        pass
