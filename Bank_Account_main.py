from Bank_account import Changepassword
from Bank_account import customer_message
from Bank_account import Amount
from Bank_account import Transaction
import time
import os
import sys
import subprocess
import re
import random as rd
from datetime import datetime
from Bank_account import get_account_number

const_email = sys.argv[1]

print("\n")
account_number,current_amount = get_account_number(const_email)
print("-----------------------------------------------------------------")
print(f"Your account number is: {account_number}")
print(f"Current  Balance: GHS {current_amount:.2f}")
print("-----------------------------------------------------------------")
print("What do you wish to do ?")
print("1.Send Money \n2.Change paswword \n3.View Transaction \n4.Customer Care  \n5.Log-out")
while True:
    command = input("Enter a choice: ")
    try:    
        com = int(command)
    except ValueError:
        print("Invalid command")
    else:
        if com == 1:
            while True:
                account_number = input("Enter the account number ? ").strip()
                if not (account_number.isdigit() and len(account_number) == 15):
                    print("Invalid account number. It must be exactly 15 digits.")
                    continue

                print("Enter amount you want to send")
                amount_text = input(": ").strip()
                try:
                    amount = float(amount_text)
                    if amount <= 0:
                        print("Amount must be greater than 0.")
                        continue
                except ValueError:
                    print("Invalid amount. Enter a numeric value.")
                    continue

                transfer = Transaction(amount, account_number)
                confirm = transfer.check()
                if not confirm:
                    continue

                remaining_balance = transfer.send(confirm)
                transaction_id = transfer.transaction_generator()
                if transaction_id is None:
                    transaction_id = "N/A"
                now = datetime.now()
                date_text = now.strftime("%Y-%m-%d")
                time_text = now.strftime("%H:%M:%S")
                if remaining_balance is None:
                    remaining_balance = "N/A"
                print(
                    f"Your transfer of {amount:.2f} GHS to {account_number} was successful on {date_text} at {time_text}.\n"
                    f"Transaction Reference: {transaction_id}\n"
                    f"Payment Method: Bank Transfer\n"
                    f"Remaining Balance: {remaining_balance} GHS\n"
                    "If you did not initiate this transaction, contact support immediately."
                )
                break



                    
        if com == 2:
            def codegenerater():
                numrange = [x for x in range(1,11)]
                confidential_code= rd.sample(numrange,k=6)
                rd.shuffle(confidential_code) 
                code =str()
                for each_number in confidential_code:
                    code += str(each_number)
                return code 
            actual_code = codegenerater()
            print("We've sent a One-Time Password (OTP) to your registered email address. Please check your inbox and enter the code below to proceed.\nThe code expires in 10 minutes. If you don't see it, check your spam or junk folder.\n")
            starter = Changepassword("jamesaningtaylor@gmail.com","4545",actual_code)
            starter.confirm_email()
            while True:
                nex_command = input("Didn't receive a code? [Resend Code] (Y/N): ")
                if nex_command.upper() == "Y":
                    print("We've sent a One-Time Password (OTP) to your registered email address. Please check your inbox and enter the code below to proceed.\nThe code expires in 10 minutes. If you don't see it, check your spam or junk folder.\n")
                    starter.confirm_email()
                elif nex_command.upper() == "N":
                    print("Enter the code recieved")
                    confirmed_code = input(": ")
                    if actual_code != confirmed_code:
                        print("The code is incorrect\n")
                    else:
                        req = re.compile(r"[A-Za-z0-9!.{}/+-_]{8,20}")
                        while True:
                            new_password = input("Enter your new password: ")
                            match = req.match(new_password)
                            if match == None:
                                print("Invalid password create a strong password")
                            else:
                                print("wait while we update your password")
                                time.sleep(3)
                                start = Changepassword(email=const_email,new_pin=new_password,code=actual_code)
                                starter.change()
                                break

                        break
                else:
                    print("Invalid Command enter command again")
                
        if com == 3:
            print("Wait while we generate a  statistics of your transaction and a visual \n")


        if com == 4:
            print("Hi there! Need help with your account or have a question? Just reply to this message or send us an email — our Customer Care team is here for you and will respond shortly.")
            print("Enter (Y/N) to proceed")
            while True:
                request_command = input(": ")
                if request_command.upper() == "N":
                    print("Thank You!")
                    break
                else:
                    help_message = input("Enter your message here: ")
                    print("Do you wish to send this message (Y/N)")
                    confirm_command = input(": ")
                    if confirm_command.upper() == 'Y':
                        customer_message(help_message)
                        print("Message is sent successfully and we will attend to you shortly")
                        break
                    elif confirm_command.upper() == "N":
                        print("Your resquest to send a message is cancelled \n")
                        break
                    else:
                        print("Invalid command")
                        break
                
        if com == 5:
            print("Thanks for your services")
            break
        
