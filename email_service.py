import smtplib
from datetime import datetime

BANK_EMAIL = "jackhenrykofiobuobilarbi@gmail.com"
BANK_EMAIL_PASSWORD = "nqxq rlam qzzk wpwr"


def _send(to_email, subject, body):
    msg = (
        f"Subject: {subject}\n"
        f"From: {BANK_EMAIL}\n"
        f"To: {to_email}\n"
        f"Reply-To: no-reply@gmail.com\n"
        f"MIME-Version: 1.0\n"
        f"Content-Type: text/plain; charset=utf-8\n"
        f"Content-Transfer-Encoding: 8bit\n"
        f"\n{body}"
    )
    try:
        smtObject = smtplib.SMTP_SSL("smtp.gmail.com", 465)
        smtObject.ehlo()
        smtObject.login(BANK_EMAIL, BANK_EMAIL_PASSWORD)
        smtObject.sendmail(BANK_EMAIL, to_email, msg.encode("utf-8"))
        smtObject.quit()
        print("Email sent successfully!")
        return True
    except smtplib.SMTPAuthenticationError:
        print("ERROR: Email authentication failed. Check credentials / app password.")
        return False
    except smtplib.SMTPException as e:
        print(f"ERROR: Email sending failed. {e}")
        return False
    except Exception as e:
        print(f"ERROR: {e}")
        return False


def send_otp(to_email, otp_code):
    body = (
        f"One-Time Password Reset Code — Action Required\n\n"
        f"We received a request to reset your password.\n"
        f"Reset Code: {otp_code}\n\n"
        f"This code expires in 10 minutes and is for single use only.\n"
        f"Never share it with anyone.\n\n"
        f"If you did not request this, please ignore this message.\n"
        f"Your password remains unchanged."
    )
    return _send(to_email, "Access Bank — Password Reset OTP", body)


def send_transaction_confirmation(to_email, amount, recipient, txn_id, remaining):
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    body = (
        f"Transaction Confirmation — Access Bank\n\n"
        f"Amount Sent      : GHS {amount:.2f}\n"
        f"To Account       : {recipient}\n"
        f"Transaction ID   : {txn_id}\n"
        f"Date & Time      : {now}\n"
        f"Remaining Balance: GHS {remaining:.2f}\n\n"
        f"Payment Method   : Bank Transfer\n\n"
        f"If you did not initiate this transaction, contact support immediately."
    )
    return _send(to_email, "Transaction Confirmation — Access Bank", body)


def send_welcome(to_email, name, account_id, bank_username):
    body = (
        f"Welcome to Access Bank, {name}!\n\n"
        f"Your account has been successfully created.\n\n"
        f"Bank Username  : {bank_username}\n"
        f"Account Number : {account_id}\n\n"
        f"Please keep your credentials safe.\n\n"
        f"Thank you for choosing Access Bank."
    )
    return _send(to_email, "Welcome to Access Bank", body)


if __name__ == "__main__":
    import sys

    print("Access Bank — Email Service Test")
    print("=" * 40)
    to = input("Recipient email address: ").strip()
    print("\nChoose email type:")
    print("1. OTP / Password Reset")
    print("2. Transaction Confirmation")
    print("3. Welcome Email")
    choice = input("Enter choice (1/2/3): ").strip()

    if choice == "1":
        code = input("OTP code to send: ").strip()
        send_otp(to, code)
    elif choice == "2":
        amount    = float(input("Amount (GHS): ").strip())
        recipient = input("Recipient account number: ").strip()
        txn_id    = input("Transaction ID: ").strip()
        remaining = float(input("Remaining balance (GHS): ").strip())
        send_transaction_confirmation(to, amount, recipient, txn_id, remaining)
    elif choice == "3":
        name       = input("Customer name: ").strip()
        account_id = input("Account number: ").strip()
        username   = input("Bank username: ").strip()
        send_welcome(to, name, account_id, username)
    else:
        print("Invalid choice.")
        sys.exit(1)
