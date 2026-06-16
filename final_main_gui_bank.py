"""
Access Bank – Final Integrated GUI
Integrates all logic from:
  • Bank_bulid_1.py  (registration, login, password generator, send_email)
  • Bank_account.py  (Transaction, Changepassword, Amount, customer_message)
  • Bank_interface.py (registration validations, username generation)
  • Bank_Account_main.py (dashboard: send money, OTP change password, customer care)
Single self-contained file.
"""

import sys
import os
import re
import time
import random
import string
import sqlite3
import smtplib
from datetime import datetime
from email.message import EmailMessage

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QDialog, QMessageBox, QComboBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QSpinBox, QDoubleSpinBox,
    QTextEdit, QFormLayout, QGroupBox, QStackedWidget, QAction,
    QHeaderView, QFrame, QSizePolicy
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QColor, QPalette

try:
    import docx as _docx
    DOCX_AVAILABLE = True
except ImportError:
    DOCX_AVAILABLE = False

# ── Bank credentials (single source of truth) ────────────────────────────────
BANK_EMAIL = "jackhenrykofiobuobilarbi@gmail.com"
BANK_EMAIL_PASSWORD = "nqxq rlam qzzk wpwr"
DB_FILE = "Bank_JH.db"


# ═══════════════════════════════════════════════════════════════════════════════
#  DATABASE  (from Bank_bulid_1.py + Bank_account.py)
# ═══════════════════════════════════════════════════════════════════════════════
class DB:
    @staticmethod
    def init():
        """Ensure all required tables exist — safe to call on every startup."""
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Customer_services(
                Customer_Name     TEXT NOT NULL,
                Customer_Age      TEXT NOT NULL,
                Customer_Gender   TEXT NOT NULL,
                Customer_Status   TEXT NOT NULL,
                Customer_Location TEXT NOT NULL,
                Customer_Phone    TEXT NOT NULL,
                Customer_Email    TEXT NOT NULL UNIQUE PRIMARY KEY,
                Customer_password TEXT NOT NULL,
                Customer_ID       INT  NOT NULL UNIQUE
            )''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Account(
                Account_id       TEXT PRIMARY KEY,
                Customer_ID      INT,
                Current_amount   REAL DEFAULT 0,
                Transaction_Date TEXT,
                Transaction_ID   TEXT
            )''')
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Transactions(
                Transaction_ID   TEXT PRIMARY KEY,
                From_Account     TEXT,
                To_Account       TEXT,
                Amount           REAL,
                Transaction_Date TEXT,
                Status           TEXT
            )''')
        conn.commit()
        conn.close()

    @staticmethod
    def get_customer(email):
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT * FROM Customer_services WHERE Customer_Email = ?", (email,))
        row = cur.fetchone()
        conn.close()
        return row

    @staticmethod
    def get_account(customer_id):
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT * FROM Account WHERE Customer_ID = ?", (customer_id,))
        row = cur.fetchone()
        conn.close()
        return row

    @staticmethod
    def get_transactions(account_id):
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute('''
            SELECT * FROM Transactions
            WHERE From_Account = ? OR To_Account = ?
            ORDER BY Transaction_Date DESC
        ''', (str(account_id), str(account_id)))
        rows = cur.fetchall()
        conn.close()
        return rows

    @staticmethod
    def login(email, password):
        """Return True if credentials match (mirrors Bank_bulid_1.check())."""
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT Customer_password FROM Customer_services WHERE Customer_Email = ?", (email,))
        data = cur.fetchone()
        conn.close()
        return data is not None and password == data[0]

    @staticmethod
    def is_duplicate(email):
        """Return True if email already registered (mirrors Sign_up_check.check())."""
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT Customer_Email FROM Customer_services WHERE Customer_Email = ?", (email,))
        result = cur.fetchone()
        conn.close()
        return result is not None

    @staticmethod
    def register(name, age, gender, status, location, phone, email, password, account_id):
        """
        Register a new customer and create their Account row.
        Mirrors Register_Identity.register() / register_not() from Bank_bulid_1.py.
        """
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO Customer_services(
                Customer_Name, Customer_Age, Customer_Gender, Customer_Status,
                Customer_Location, Customer_Phone, Customer_Email,
                Customer_password, Customer_ID)
            VALUES(?,?,?,?,?,?,?,?,?)
        ''', (name, str(age), gender, status, location, phone, email, password, account_id))
        cur.execute('''
            CREATE TABLE IF NOT EXISTS Account(
                Account_id TEXT PRIMARY KEY, Customer_ID INT,
                Current_amount REAL DEFAULT 0,
                Transaction_Date TEXT, Transaction_ID TEXT)
        ''')
        cur.execute('''
            INSERT INTO Account(Account_id, Customer_ID, Current_amount,
                                Transaction_Date, Transaction_ID)
            VALUES(?,?,?,?,?)
        ''', (str(account_id), account_id, 0.0, None, None))
        conn.commit()
        conn.close()
        # Write text report (mirrors Bank_bulid_1.py report file)
        with open("Bank_JH.txt", "a") as f:
            f.write(
                f"{name}\n{age}\n{gender}\n{status}\n"
                f"{location}\n{phone}\n{email}\n{password}\n{account_id}\n---\n"
            )

    @staticmethod
    def update_password(email, new_password):
        """Mirrors Changepassword.change() from Bank_account.py."""
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute(
            "UPDATE Customer_services SET Customer_password = ? WHERE Customer_Email = ?",
            (new_password, email)
        )
        conn.commit()
        conn.close()

    @staticmethod
    def transfer(sender_id, recipient_id, amount):
        """
        Deduct from sender, credit recipient.
        Mirrors Transaction.check() + Transaction.send() from Bank_account.py.
        Returns (new_balance, error_message).
        """
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT Current_amount FROM Account WHERE Account_id = ?", (str(sender_id),))
        row = cur.fetchone()
        if row is None:
            conn.close()
            return None, "Sender account not found."
        if float(row[0]) < amount:
            conn.close()
            return None, "Insufficient funds. Please recharge!"
        cur.execute("SELECT Account_id FROM Account WHERE Account_id = ?", (str(recipient_id),))
        if cur.fetchone() is None:
            conn.close()
            return None, "Recipient account not found."
        cur.execute(
            "UPDATE Account SET Current_amount = Current_amount - ? WHERE Account_id = ?",
            (amount, str(sender_id))
        )
        cur.execute(
            "UPDATE Account SET Current_amount = Current_amount + ? WHERE Account_id = ?",
            (amount, str(recipient_id))
        )
        cur.execute("SELECT Current_amount FROM Account WHERE Account_id = ?", (str(sender_id),))
        new_balance = cur.fetchone()[0]
        conn.commit()
        conn.close()
        return new_balance, None

    @staticmethod
    def record_transaction(txn_id, from_account, to_account, amount):
        """
        Persist a completed transfer.
        Mirrors Transaction.transaction_record() from Bank_account.py.
        """
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute('''
            INSERT INTO Transactions(
                Transaction_ID, From_Account, To_Account,
                Amount, Transaction_Date, Status)
            VALUES(?,?,?,?,?,?)
        ''', (str(txn_id), str(from_account), str(to_account), amount, now, "Completed"))
        conn.commit()
        conn.close()
        # Also write text report (mirrors Transaction.transaction_report())
        with open("Bank_Transaction.txt", "a") as f:
            f.write(
                f"Transaction Initiated\n"
                f"Account {from_account} sent GHc{amount:.2f} at {now}\n"
                f"Transaction Successful\n---\n"
            )

    @staticmethod
    def deposit(account_id, amount):
        """Credit an account with the deposit amount. Returns (new_balance, error)."""
        conn = sqlite3.connect(DB_FILE)
        cur = conn.cursor()
        cur.execute("SELECT Account_id FROM Account WHERE Account_id = ?", (str(account_id),))
        if cur.fetchone() is None:
            conn.close()
            return None, "Account not found."
        cur.execute(
            "UPDATE Account SET Current_amount = Current_amount + ? WHERE Account_id = ?",
            (amount, str(account_id))
        )
        cur.execute("SELECT Current_amount FROM Account WHERE Account_id = ?", (str(account_id),))
        new_balance = cur.fetchone()[0]
        conn.commit()
        conn.close()
        return new_balance, None


# ═══════════════════════════════════════════════════════════════════════════════
#  EMAIL SERVICE  (from Bank_account.py Changepassword + send_email)
# ═══════════════════════════════════════════════════════════════════════════════
class EmailService:
    @staticmethod
    def _send(to_email, subject, body):
        msg = f"Subject: {subject}\nFrom: {BANK_EMAIL}\nTo: {to_email}\nReply-To: no-reply@gmail.com\n\n{body}"
        try:
            smtObject = smtplib.SMTP_SSL("smtp.gmail.com", 465)
            smtObject.ehlo()
            smtObject.login(BANK_EMAIL, BANK_EMAIL_PASSWORD)
            smtObject.sendmail(BANK_EMAIL, to_email, msg.encode("utf-8"))
            smtObject.quit()
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

    @staticmethod
    def send_otp(to_email, otp_code):
        """Mirrors Changepassword.confirm_email() from Bank_account.py."""
        body = (
            f"One-Time Password Reset Code — Action Required\n\n"
            f"We received a request to reset your password.\n"
            f"Reset Code: {otp_code}\n\n"
            f"This code expires in 10 minutes and is for single use only.\n"
            f"Never share it with anyone.\n\n"
            f"If you did not request this, please ignore this message.\n"
            f"Your password remains unchanged."
        )
        return EmailService._send(to_email, "Access Bank — Password Reset OTP", body)

    @staticmethod
    def send_transaction_confirmation(to_email, amount, recipient, txn_id, remaining):
        """Email confirmation after a successful transfer."""
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
        EmailService._send(to_email, "Transaction Confirmation — Access Bank", body)

    @staticmethod
    def send_welcome(to_email, name, account_id, bank_username):
        """Welcome email on successful registration (mirrors send_email.send())."""
        body = (
            f"Welcome to Access Bank, {name}!\n\n"
            f"Your account has been successfully created.\n\n"
            f"Bank Username  : {bank_username}\n"
            f"Account Number : {account_id}\n\n"
            f"Please keep your credentials safe.\n\n"
            f"Thank you for choosing Access Bank."
        )
        EmailService._send(to_email, "Welcome to Access Bank", body)

    @staticmethod
    def send_deposit_otp(to_email, otp_code, amount):
        """OTP authorization email sent before a deposit is processed."""
        body = (
            f"Deposit Authorization — Access Bank\n\n"
            f"A deposit of GHS {amount:.2f} has been requested on your account.\n\n"
            f"Authorization Code: {otp_code}\n\n"
            f"This code expires in 10 minutes and is for single use only.\n"
            f"Never share it with anyone.\n\n"
            f"If you did not initiate this deposit, please contact support immediately."
        )
        return EmailService._send(to_email, "Access Bank — Deposit Authorization OTP", body)

    @staticmethod
    def send_deposit_confirmation(to_email, amount, txn_id, new_balance):
        """Confirmation email after a successful deposit."""
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        body = (
            f"Deposit Confirmation — Access Bank\n\n"
            f"Amount Deposited : GHS {amount:.2f}\n"
            f"Transaction ID   : {txn_id}\n"
            f"Date & Time      : {now}\n"
            f"New Balance      : GHS {new_balance:.2f}\n\n"
            f"Your deposit has been processed successfully.\n\n"
            f"If you did not initiate this transaction, contact support immediately."
        )
        EmailService._send(to_email, "Deposit Confirmation — Access Bank", body)


# ═══════════════════════════════════════════════════════════════════════════════
#  UTILITY FUNCTIONS  (from all source files)
# ═══════════════════════════════════════════════════════════════════════════════
def generate_account_id():
    """15-digit account number. Mirrors Register_Identity._generate_account_id()."""
    digits = list(range(1, 10))
    full = random.sample(digits, 9) + random.sample(digits, 6)
    return int("".join(str(d) for d in full))

def generate_bank_username(full_name):
    """
    Derive bank username from name (mirrors Bank_interface.py logic).
    e.g. "John Henry Doe" → "jhdjohn"
    """
    parts = full_name.strip().split()
    initials = "".join(p[0].lower() for p in parts)
    return initials + parts[0].lower()

def generate_otp():
    """6-digit OTP. Mirrors Bank_Account_main.py codegenerater()."""
    digits = list(range(1, 10))
    return "".join(str(d) for d in random.sample(digits, 6))

def generate_strong_password():
    """Mirrors Passwordgenerator.generate() from Bank_bulid_1.py."""
    WORDs = random.sample(string.ascii_uppercase, k=3)
    wrd   = random.sample(string.ascii_lowercase, k=3)
    nums  = random.sample("1234567890", k=2)
    syms  = random.sample("!£$%^&*()_+}{?/", k=2)
    combined = WORDs + wrd + syms + nums
    random.shuffle(combined)
    return "".join(combined)

def generate_transaction_id():
    """Mirrors Transaction.transaction_generator() from Bank_account.py."""
    sample = random.sample(range(1, 10), 9)
    random.shuffle(sample)
    return int("".join(str(c) for c in sample))

def save_customer_message(msg: str):
    """
    Append customer care message to docx report.
    Mirrors customer_message() from Bank_account.py.
    """
    if not DOCX_AVAILABLE:
        raise RuntimeError("python-docx is not installed. Run: pip install python-docx")
    filename = "Bank_customer_report.docx"
    if not os.path.exists(filename):
        doc = _docx.Document()
        para = doc.add_paragraph("-------------------Report----------------")
        para.add_run("\n" + msg)
        doc.save(filename)
    else:
        doc = _docx.Document(filename)
        para = doc.add_paragraph("-------------------Report----------------")
        para.add_run(msg)
        doc.save(filename)


# ═══════════════════════════════════════════════════════════════════════════════
#  SHARED STYLES
# ═══════════════════════════════════════════════════════════════════════════════
SIDEBAR_STYLE = """
QWidget {
    background-color: #2c3e50;
    color: white;
}
QPushButton {
    background-color: #34495e;
    color: white;
    border: none;
    padding: 10px 18px;
    text-align: left;
    font-size: 13px;
    border-radius: 4px;
    font-weight: bold;
}
QPushButton:hover  { background-color: #007bff; color: #ffffff; }
QPushButton:checked { background-color: #007bff; color: #ffffff; font-weight: bold; }
"""

APP_STYLE = """
QMainWindow, QWidget { background-color: #f5f5f5; color: #333333; }
QLineEdit, QTextEdit, QSpinBox, QDoubleSpinBox, QComboBox {
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 8px;
    background-color: #ffffff;
    font-size: 13px;
    color: #333333;
}
QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border: 2px solid #007bff;
    background-color: white;
}
QGroupBox {
    border: 1px solid #ddd;
    border-radius: 4px;
    padding: 10px;
    margin-top: 10px;
    background-color: #ffffff;
    font-weight: bold;
    color: #555555;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 0 3px;
}
QTableWidget {
    background-color: #ffffff;
    border: 1px solid #ddd;
    border-radius: 4px;
    font-size: 12px;
}
QTableWidget::item          { padding: 5px; }
QTableWidget::item:selected { background-color: #cce5ff; color: #333333; }
QHeaderView::section {
    background-color: #f8f9fa;
    border: none;
    border-bottom: 1px solid #ddd;
    padding: 8px;
    font-weight: bold;
    color: #555555;
}
QTabWidget::pane { border: 1px solid #ddd; }
QTabBar::tab {
    background-color: #e9ecef;
    padding: 8px 20px;
    border: 1px solid #ddd;
}
QTabBar::tab:selected { background-color: white; border-bottom: 2px solid #007bff; }
"""

def _btn(text, color="#007bff", hover="#0056b3", height=40):
    b = QPushButton(text)
    b.setMinimumHeight(height)
    b.setStyleSheet(f"""
        QPushButton {{
            background-color: {color};
            color: white;
            border: none;
            border-radius: 6px;
            padding: 10px 20px;
            font-weight: bold;
            font-size: 13px;
        }}
        QPushButton:hover   {{ background-color: {hover}; }}
        QPushButton:pressed {{ background-color: #003d82; }}
    """)
    return b

def primary_btn(text, height=40):  return _btn(text, "#007bff", "#0056b3", height)
def success_btn(text, height=40):  return _btn(text, "#28a745", "#218838", height)
def warning_btn(text, height=40):  return _btn(text, "#ffc107", "#e0a800", height)
def danger_btn(text, height=40):   return _btn(text, "#dc3545", "#c82333", height)
def purple_btn(text, height=40):   return _btn(text, "#6f42c1", "#5a32a3", height)


# ═══════════════════════════════════════════════════════════════════════════════
#  OTP DIALOG
# ═══════════════════════════════════════════════════════════════════════════════
class OTPDialog(QDialog):
    """
    Modal OTP verification dialog.
    Mirrors the OTP flow from Bank_Account_main.py (com == 2) and
    Bank_account.py Changepassword.confirm_email().
    """
    def __init__(self, email, otp_code, parent=None):
        super().__init__(parent)
        self.email    = email
        self.otp_code = otp_code
        self.verified = False
        self.setWindowTitle("OTP Verification — Access Bank")
        self.setModal(True)
        self.resize(430, 300)
        self.setStyleSheet(APP_STYLE)
        self._build()

    def _build(self):
        layout = QVBoxLayout()
        layout.setContentsMargins(28, 24, 28, 24)
        layout.setSpacing(14)

        heading = QLabel("Verify Your Identity")
        heading.setFont(QFont("Arial", 15, QFont.Bold))
        layout.addWidget(heading)

        info = QLabel(
            f"A 6-digit One-Time Password has been sent to:\n"
            f"{self.email}\n\n"
            "Enter the code below. It expires in 10 minutes.\n"
            "If you didn't receive it, click Resend."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #4a5568; font-size: 12px;")
        layout.addWidget(info)

        self.code_input = QLineEdit()
        self.code_input.setPlaceholderText("Enter OTP code")
        self.code_input.setMaxLength(10)
        self.code_input.setAlignment(Qt.AlignCenter)
        self.code_input.setStyleSheet(
            "font-size: 20px; letter-spacing: 6px; padding: 10px; border: 2px solid #3182ce;"
        )
        layout.addWidget(self.code_input)

        row = QHBoxLayout()
        resend = QPushButton("Resend Code")
        resend.setStyleSheet(
            "color:#3182ce; border:none; background:transparent; font-size:12px; padding:4px;"
        )
        resend.clicked.connect(self._resend)
        verify = primary_btn("Verify & Continue", 40)
        verify.clicked.connect(self._verify)
        row.addWidget(resend)
        row.addStretch()
        row.addWidget(verify)
        layout.addLayout(row)
        self.setLayout(layout)

    def _verify(self):
        if self.code_input.text().strip() == self.otp_code:
            self.verified = True
            self.accept()
        else:
            QMessageBox.warning(self, "Wrong Code",
                "The code you entered is incorrect.\nPlease try again or click Resend.")

    def _resend(self):
        EmailService.send_otp(self.email, self.otp_code)
        QMessageBox.information(self, "Code Resent",
            "A new OTP has been sent to your email.\n"
            "If you don't see it, check your spam folder.")


# ═══════════════════════════════════════════════════════════════════════════════
#  AUTH WINDOW  (Login + Register — from Bank_interface.py + Bank_bulid_1.py)
# ═══════════════════════════════════════════════════════════════════════════════
class AuthWindow(QWidget):
    """
    Combined login / registration window.
    Carries all validations from Bank_interface.py and Bank_bulid_1.py.
    """
    login_success = pyqtSignal(str)   # emits the logged-in email

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Access Bank — Welcome")
        self.setGeometry(100, 100, 540, 680)
        self.setStyleSheet(APP_STYLE)
        self._build()

    def _build(self):
        root = QVBoxLayout()
        root.setContentsMargins(44, 30, 44, 30)
        root.setSpacing(4)

        # Bank header (mirrors Bank_bulid_1.greet())
        title = QLabel("ACCESS BANK")
        title.setFont(QFont("Arial", 28, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #007bff; letter-spacing: 4px;")
        root.addWidget(title)

        sub = QLabel("Secure Banking Solutions")
        sub.setAlignment(Qt.AlignCenter)
        sub.setStyleSheet("color: #666666; font-size: 12px; margin-bottom: 16px;")
        root.addWidget(sub)

        tabs = QTabWidget()
        tabs.addTab(self._login_tab(),    "Sign In")
        tabs.addTab(self._register_tab(), "Create Account")
        root.addWidget(tabs)
        self.setLayout(root)

    # ── Login tab ──────────────────────────────────────────────────────────────
    def _login_tab(self):
        w = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(10)
        layout.setContentsMargins(10, 20, 10, 10)

        layout.addWidget(QLabel("Email Address"))
        self.login_email = QLineEdit()
        self.login_email.setPlaceholderText("yourname@example.com")
        layout.addWidget(self.login_email)

        layout.addWidget(QLabel("Password"))
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Enter your password")
        self.login_password.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.login_password)

        btn = primary_btn("Sign In", 46)
        btn.clicked.connect(self._handle_login)
        layout.addSpacing(10)
        layout.addWidget(btn)
        layout.addStretch()
        w.setLayout(layout)
        return w

    # ── Register tab ───────────────────────────────────────────────────────────
    def _register_tab(self):
        w = QWidget()
        layout = QVBoxLayout()
        layout.setSpacing(8)
        layout.setContentsMargins(10, 12, 10, 10)

        def row(label, widget):
            layout.addWidget(QLabel(label))
            layout.addWidget(widget)

        self.reg_name = QLineEdit()
        self.reg_name.setPlaceholderText("e.g. John Henry Doe  (each word 3–8 letters)")
        row("Full Name *", self.reg_name)

        self.reg_age = QSpinBox()
        self.reg_age.setRange(1, 119)
        row("Age *", self.reg_age)

        self.reg_gender = QComboBox()
        self.reg_gender.addItems(["Male", "Female"])
        row("Gender *", self.reg_gender)

        self.reg_status = QComboBox()
        self.reg_status.addItems(["Single", "Married", "Student"])
        row("Status *", self.reg_status)

        self.reg_location = QLineEdit()
        self.reg_location.setPlaceholderText("Town/City (letters only)")
        row("Location *", self.reg_location)

        self.reg_phone = QLineEdit()
        self.reg_phone.setPlaceholderText("050-000-0000")
        row("Phone *", self.reg_phone)

        self.reg_email = QLineEdit()
        self.reg_email.setPlaceholderText("yourname@example.com")
        row("Email *", self.reg_email)

        # Password + Generate button
        layout.addWidget(QLabel("Password *  (8–20 chars, letters/digits/special)"))
        pwd_row = QHBoxLayout()
        self.reg_password = QLineEdit()
        self.reg_password.setPlaceholderText("Create a strong password")
        self.reg_password.setEchoMode(QLineEdit.Password)
        gen_btn = QPushButton("Generate")
        gen_btn.setFixedWidth(86)
        gen_btn.setStyleSheet(
            "background:#e2e8f0; border-radius:6px; padding:8px; font-size:11px; color:#2d3748;"
        )
        gen_btn.clicked.connect(self._generate_password)
        pwd_row.addWidget(self.reg_password)
        pwd_row.addWidget(gen_btn)
        layout.addLayout(pwd_row)

        self.reg_confirm = QLineEdit()
        self.reg_confirm.setPlaceholderText("Re-enter password")
        self.reg_confirm.setEchoMode(QLineEdit.Password)
        row("Confirm Password *", self.reg_confirm)

        btn = primary_btn("Create Account", 46)
        btn.clicked.connect(self._handle_register)
        layout.addSpacing(8)
        layout.addWidget(btn)
        w.setLayout(layout)
        return w

    def _generate_password(self):
        """Mirrors Passwordgenerator.generate() from Bank_bulid_1.py."""
        pwd = generate_strong_password()
        self.reg_password.setText(pwd)
        self.reg_password.setEchoMode(QLineEdit.Normal)
        self.reg_confirm.setText(pwd)
        QMessageBox.information(self, "Password Generated",
            f"Your generated password:\n\n{pwd}\n\n"
            "Please copy and save it somewhere safe before continuing.")

    # ── Login handler ──────────────────────────────────────────────────────────
    def _handle_login(self):
        email    = self.login_email.text().strip()
        password = self.login_password.text().strip()

        if not email or not password:
            QMessageBox.warning(self, "Missing Fields", "Please enter your email and password.")
            return
        if not re.match(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}", email):
            QMessageBox.warning(self, "Invalid Email", "Please enter a valid email address.")
            return

        # Mirrors Bank_bulid_1.check()
        if DB.login(email, password):
            self.login_email.clear()
            self.login_password.clear()
            self.login_success.emit(email)
        else:
            QMessageBox.critical(self, "Login Failed",
                "Invalid email or password.\nPlease try again or create an account.")

    # ── Register handler ───────────────────────────────────────────────────────
    def _handle_register(self):
        """
        Full validation chain from Bank_interface.py:
        name words (3-8 alpha), phone format, location alpha,
        email regex, strong password (8-20 chars), confirmation,
        duplicate check via Sign_up_check equivalent.
        """
        name     = self.reg_name.text().strip()
        age      = self.reg_age.value()
        gender   = self.reg_gender.currentText()
        status   = self.reg_status.currentText()
        location = self.reg_location.text().strip()
        phone    = self.reg_phone.text().strip()
        email    = self.reg_email.text().strip()
        password = self.reg_password.text().strip()
        confirm  = self.reg_confirm.text().strip()

        if not all([name, phone, email, password, confirm, location]):
            QMessageBox.warning(self, "Missing Fields", "Please fill in all required fields (*).")
            return

        # Each word in name: 3-8 alpha chars (from Bank_interface.py)
        name_re = re.compile(r"^[a-zA-Z]{3,8}$")
        for part in name.split():
            if not name_re.match(part):
                QMessageBox.warning(self, "Invalid Name",
                    "Each word in your name must be 3–8 letters only.\n"
                    "No numbers, spaces at the end, or special characters.")
                return

        # Phone format: 050-000-0000 (from Bank_interface.py)
        if not re.match(r"^\d{3}-\d{3}-\d{4}$", phone):
            QMessageBox.warning(self, "Invalid Phone",
                "Phone number must follow the format: 050-000-0000")
            return

        # Location: letters only (from Bank_interface.py)
        if not location.isalpha():
            QMessageBox.warning(self, "Invalid Location",
                "Location must contain letters only (no spaces, numbers, or special characters).")
            return

        # Email (from Bank_interface.py)
        if not re.match(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}", email):
            QMessageBox.warning(self, "Invalid Email",
                "Email must contain '@' and '.' e.g. name@domain.com")
            return

        # Strong password: 8-20 chars (from Bank_interface.py)
        if not re.match(r"[a-zA-Z0-9.!£$%^&*()_+|]{8,20}$", password):
            QMessageBox.warning(self, "Weak Password",
                "Password must be 8–20 characters using letters, digits, or\n"
                "special characters: !£$%^&*()_+|")
            return

        # Confirm match
        if password != confirm:
            QMessageBox.warning(self, "Password Mismatch", "Passwords do not match.")
            return

        # Duplicate check (mirrors Sign_up_check from Bank_bulid_1.py)
        if DB.is_duplicate(email):
            QMessageBox.warning(self, "Account Exists",
                "An account with this email already exists.\nPlease sign in instead.")
            return

        try:
            account_id    = generate_account_id()
            bank_username = generate_bank_username(name)   # from Bank_interface.py logic

            # Mirrors Register_Identity.register() / register_not()
            DB.register(name, age, gender, status, location, phone, email, password, account_id)

            # Welcome email (mirrors send_email.send() from Bank_bulid_1.py)
            EmailService.send_welcome(email, name, account_id, bank_username)

            QMessageBox.information(self, "Account Created — Welcome!",
                f"Your Access Bank account is ready!\n\n"
                f"Bank Username  : {bank_username}\n"
                f"Account Number : {account_id}\n\n"
                "Please save these details. You can now sign in.")

            for field in [self.reg_name, self.reg_location, self.reg_phone,
                          self.reg_email, self.reg_password, self.reg_confirm]:
                field.clear()

        except Exception as e:
            QMessageBox.critical(self, "Registration Error",
                f"Could not create account:\n{str(e)}")


# ═══════════════════════════════════════════════════════════════════════════════
#  DASHBOARD  (post-login — from Bank_Account_main.py)
# ═══════════════════════════════════════════════════════════════════════════════
class Dashboard(QMainWindow):
    """
    Full post-login dashboard.
    Mirrors all options from Bank_Account_main.py:
      1. Send Money           → Transfer page
      2. Change Password (OTP)→ Change Password page
      3. View Transactions    → History page  (was a stub in original)
      4. Customer Care        → Customer Care page
      5. Logout               → back to AuthWindow
    Plus: Profile page with account info & password generator tool.
    """
    def __init__(self, email: str):
        super().__init__()
        self.email    = email
        self.customer = DB.get_customer(email)
        self.account  = DB.get_account(self.customer[8]) if self.customer else None
        self.setWindowTitle(f"Access Bank — {self.customer[0] if self.customer else email}")
        self.setGeometry(80, 50, 1120, 730)
        self.setStyleSheet(APP_STYLE)
        self._build()
        self._refresh_transactions()

    def _build(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout()
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)
        self.pages = QStackedWidget()
        self.pages.addWidget(self._overview_page())       # 0
        self.pages.addWidget(self._transfer_page())       # 1
        self.pages.addWidget(self._history_page())        # 2
        self.pages.addWidget(self._change_pwd_page())     # 3
        self.pages.addWidget(self._customer_care_page())  # 4
        self.pages.addWidget(self._profile_page())        # 5
        self.pages.addWidget(self._deposit_page())        # 6

        root.addWidget(self._sidebar())
        root.addWidget(self.pages, 1)
        central.setLayout(root)

    # ── Sidebar ────────────────────────────────────────────────────────────────
    def _sidebar(self):
        sb = QWidget()
        sb.setFixedWidth(226)
        sb.setStyleSheet(SIDEBAR_STYLE)
        layout = QVBoxLayout()
        layout.setContentsMargins(12, 0, 12, 20)
        layout.setSpacing(2)

        # Bank title (mirrors Bank_bulid_1.greet())
        title = QLabel("ACCESS BANK")
        title.setFont(QFont("Arial", 18, QFont.Bold))
        title.setStyleSheet("color: #ffffff; padding: 22px 10px 4px 10px; letter-spacing: 3px;")
        layout.addWidget(title)

        name_lbl = QLabel(self.customer[0] if self.customer else "")
        name_lbl.setStyleSheet("color: #aaaaaa; font-size: 11px; padding: 0 10px 16px 10px;")
        layout.addWidget(name_lbl)

        sep = QFrame()
        sep.setFrameShape(QFrame.HLine)
        sep.setStyleSheet("color: #3d566e; margin: 0 4px 10px 4px;")
        layout.addWidget(sep)

        nav_items = [
            ("   Overview",             0),
            ("   Send Money",           1),
            ("   Deposit Money",        6),
            ("   Transaction History",  2),
            ("   Change Password",      3),
            ("   Customer Care",        4),
            ("   My Profile",           5),
        ]
        self._nav_btns = []
        for label, idx in nav_items:
            btn = QPushButton(label)
            btn.setCheckable(True)
            btn.setMinimumHeight(46)
            btn.clicked.connect(lambda _, i=idx: self._nav(i))
            self._nav_btns.append(btn)
            layout.addWidget(btn)

        layout.addStretch()

        logout = QPushButton("   Logout")
        logout.setMinimumHeight(46)
        logout.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 10px;
                font-weight: bold;
                text-align: left;
            }
            QPushButton:hover { background-color: #c82333; color: white; }
        """)
        logout.clicked.connect(self._logout)
        layout.addWidget(logout)

        sb.setLayout(layout)
        self._nav(0)
        return sb

    def _nav(self, index):
        self.pages.setCurrentIndex(index)
        for i, btn in enumerate(self._nav_btns):
            btn.setChecked(i == index)
        if index == 2:
            self._refresh_transactions()
        if index == 0:
            self._refresh_balance()

    # ── Overview page ──────────────────────────────────────────────────────────
    def _overview_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(34, 30, 34, 30)
        layout.setSpacing(22)

        name = self.customer[0] if self.customer else "Customer"
        greet = QLabel(f"Welcome back, {name}!")
        greet.setFont(QFont("Arial", 22, QFont.Bold))
        greet.setStyleSheet("color: #333333;")
        layout.addWidget(greet)

        # Balance card
        bal_card = QWidget()
        bal_card.setMinimumHeight(130)
        bal_card.setStyleSheet("""
            background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                stop:0 #007bff, stop:1 #0056b3);
            border-radius: 8px;
        """)
        bcl = QVBoxLayout()
        bcl.setContentsMargins(28, 20, 28, 20)

        lbl = QLabel("Current Balance")
        lbl.setStyleSheet("color: rgba(255,255,255,0.65); font-size: 13px;")
        bcl.addWidget(lbl)

        balance = self.account[2] if self.account and self.account[2] is not None else 0.0
        self.bal_display = QLabel(f"GHS {balance:,.2f}")
        self.bal_display.setFont(QFont("Arial", 30, QFont.Bold))
        self.bal_display.setStyleSheet("color: white;")
        bcl.addWidget(self.bal_display)

        acct_no = str(self.customer[8]) if self.customer else "N/A"
        acct_lbl = QLabel(f"Account Number: {acct_no}")
        acct_lbl.setStyleSheet("color: rgba(255,255,255,0.6); font-size: 12px;")
        bcl.addWidget(acct_lbl)

        bal_card.setLayout(bcl)
        layout.addWidget(bal_card)

        # Quick actions (mirrors Bank_Account_main.py menu)
        qa = QGroupBox("Quick Actions")
        qa_row = QHBoxLayout()
        qa_row.setSpacing(14)

        sb = primary_btn("  Send Money")
        sb.clicked.connect(lambda: self._nav(1))
        qa_row.addWidget(sb)

        db = success_btn("  Deposit Money")
        db.clicked.connect(lambda: self._nav(6))
        qa_row.addWidget(db)

        hb = warning_btn("  View Transactions")
        hb.clicked.connect(lambda: self._nav(2))
        qa_row.addWidget(hb)

        cb = purple_btn("  Customer Care")
        cb.clicked.connect(lambda: self._nav(4))
        qa_row.addWidget(cb)

        qa.setLayout(qa_row)
        layout.addWidget(qa)
        layout.addStretch()
        page.setLayout(layout)
        return page

    def _refresh_balance(self):
        if not hasattr(self, 'bal_display') or not self.customer:
            return
        acc = DB.get_account(self.customer[8])
        if acc:
            self.account = acc
            self.bal_display.setText(f"GHS {acc[2]:,.2f}")

    # ── Transfer page (mirrors Bank_Account_main.py com == 1) ─────────────────
    def _transfer_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(34, 30, 34, 30)
        layout.setSpacing(20)

        title = QLabel("Send Money")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(title)

        note = QLabel(
            "Enter the recipient's 15-digit account number and the amount to transfer.\n"
            "A confirmation email will be sent to you after the transfer."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #718096; font-size: 12px;")
        layout.addWidget(note)

        form_card = QGroupBox("Transfer Details")
        form = QFormLayout()
        form.setSpacing(14)

        self.t_recipient = QLineEdit()
        self.t_recipient.setPlaceholderText("15-digit account number")
        form.addRow("Recipient Account:", self.t_recipient)

        self.t_amount = QDoubleSpinBox()
        self.t_amount.setRange(0.01, 9999999.99)
        self.t_amount.setDecimals(2)
        self.t_amount.setPrefix("GHS ")
        form.addRow("Amount:", self.t_amount)

        self.t_desc = QLineEdit()
        self.t_desc.setPlaceholderText("Optional description / note")
        form.addRow("Description:", self.t_desc)

        form_card.setLayout(form)
        layout.addWidget(form_card)

        send_btn = primary_btn("  Send Transfer", 50)
        send_btn.clicked.connect(self._handle_transfer)
        layout.addWidget(send_btn)
        layout.addStretch()
        page.setLayout(layout)
        return page

    def _handle_transfer(self):
        recipient = self.t_recipient.text().strip()
        amount    = self.t_amount.value()

        if not recipient:
            QMessageBox.warning(self, "Missing Field", "Please enter a recipient account number.")
            return
        if not recipient.isdigit() or len(recipient) != 15:
            QMessageBox.warning(self, "Invalid Account",
                "Account number must be exactly 15 digits.")
            return
        if amount <= 0:
            QMessageBox.warning(self, "Invalid Amount", "Amount must be greater than 0.")
            return
        sender_id = str(self.customer[8])
        if recipient == sender_id:
            QMessageBox.warning(self, "Invalid", "You cannot transfer to your own account.")
            return

        # mirrors Transaction.check() + Transaction.send()
        new_balance, err = DB.transfer(sender_id, recipient, amount)
        if err:
            QMessageBox.warning(self, "Transfer Failed", err)
            return

        # mirrors Transaction.transaction_generator() + transaction_record() + transaction_report()
        txn_id = generate_transaction_id()
        DB.record_transaction(txn_id, sender_id, recipient, amount)

        # email confirmation
        EmailService.send_transaction_confirmation(self.email, amount, recipient, txn_id, new_balance)

        self.account = DB.get_account(self.customer[8])
        self._refresh_balance()

        now = datetime.now()
        QMessageBox.information(self, "Transfer Successful",
            f"Your transfer was successful!\n\n"
            f"Amount          : GHS {amount:.2f}\n"
            f"To Account      : {recipient}\n"
            f"Transaction ID  : {txn_id}\n"
            f"Date & Time     : {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Payment Method  : Bank Transfer\n"
            f"Remaining Balance: GHS {new_balance:.2f}\n\n"
            "A confirmation has been sent to your email.\n"
            "If you did not initiate this, contact support immediately.")

        self.t_recipient.clear()
        self.t_amount.setValue(0.01)
        self.t_desc.clear()
        self._refresh_transactions()

    # ── Transaction history page (was a stub in Bank_Account_main.py) ─────────
    def _history_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(34, 30, 34, 30)
        layout.setSpacing(16)

        hdr = QHBoxLayout()
        title = QLabel("Transaction History")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        hdr.addWidget(title)
        hdr.addStretch()
        ref = QPushButton("Refresh")
        ref.setStyleSheet(
            "background:#e2e8f0; border-radius:6px; padding:8px 18px; color:#2d3748;"
        )
        ref.clicked.connect(self._refresh_transactions)
        hdr.addWidget(ref)
        layout.addLayout(hdr)

        self.txn_table = QTableWidget()
        self.txn_table.setColumnCount(6)
        self.txn_table.setHorizontalHeaderLabels(
            ["Transaction ID", "From Account", "To Account", "Amount (GHS)", "Date & Time", "Status"]
        )
        self.txn_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.txn_table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.txn_table.setAlternatingRowColors(True)
        self.txn_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.txn_table.verticalHeader().setVisible(False)
        layout.addWidget(self.txn_table)
        page.setLayout(layout)
        return page

    def _refresh_transactions(self):
        if not hasattr(self, 'txn_table') or not self.customer:
            return
        rows = DB.get_transactions(str(self.customer[8]))
        self.txn_table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                item = QTableWidgetItem(
                    f"GHS {float(val):,.2f}" if c == 3 else str(val)
                )
                item.setTextAlignment(Qt.AlignCenter)
                if c == 3:
                    item.setForeground(QColor("#276749"))
                if c == 5 and str(val) == "Completed":
                    item.setForeground(QColor("#276749"))
                self.txn_table.setItem(r, c, item)

    # ── Change password page (mirrors Bank_Account_main.py com == 2) ──────────
    def _change_pwd_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(34, 30, 34, 30)
        layout.setSpacing(20)

        title = QLabel("Change Password")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(title)

        info = QLabel(
            "First verify your current password, then a One-Time Password will be sent\n"
            "to your registered email address to confirm the change."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #718096; font-size: 12px;")
        layout.addWidget(info)

        pwd_card = QGroupBox("Update Password")
        form = QFormLayout()
        form.setSpacing(14)

        self.cp_current = QLineEdit()
        self.cp_current.setEchoMode(QLineEdit.Password)
        self.cp_current.setPlaceholderText("Enter your current password")
        form.addRow("Current Password:", self.cp_current)

        self.cp_new = QLineEdit()
        self.cp_new.setEchoMode(QLineEdit.Password)
        self.cp_new.setPlaceholderText("8–20 chars: letters, digits, !.{}/+-_")
        form.addRow("New Password:", self.cp_new)

        self.cp_confirm = QLineEdit()
        self.cp_confirm.setEchoMode(QLineEdit.Password)
        self.cp_confirm.setPlaceholderText("Re-enter new password")
        form.addRow("Confirm Password:", self.cp_confirm)

        pwd_card.setLayout(form)
        layout.addWidget(pwd_card)

        update_btn = primary_btn("Update Password  (sends OTP)", 50)
        update_btn.clicked.connect(self._handle_change_pwd)
        layout.addWidget(update_btn)
        layout.addStretch()
        page.setLayout(layout)
        return page

    def _handle_change_pwd(self):
        """
        Mirrors Bank_Account_main.py com==2 with OTP flow.
        Uses Changepassword.confirm_email() logic via EmailService.send_otp()
        and Changepassword.change() logic via DB.update_password().
        """
        current = self.cp_current.text()
        new     = self.cp_new.text()
        confirm = self.cp_confirm.text()

        if not all([current, new, confirm]):
            QMessageBox.warning(self, "Missing Fields", "Please fill in all password fields.")
            return
        if not DB.login(self.email, current):
            QMessageBox.warning(self, "Wrong Password", "Your current password is incorrect.")
            return
        if new != confirm:
            QMessageBox.warning(self, "Mismatch", "New passwords do not match.")
            return
        # mirrors Bank_Account_main.py regex: r"[A-Za-z0-9!.{}/+-_]{8,20}"
        if not re.match(r"[A-Za-z0-9!.{}/+\-_]{8,20}$", new):
            QMessageBox.warning(self, "Weak Password",
                "Password must be 8–20 characters using:\nletters, digits, or !.{}/+-_")
            return

        otp = generate_otp()
        sent = EmailService.send_otp(self.email, otp)   # mirrors Changepassword.confirm_email()
        if not sent:
            QMessageBox.warning(self, "Email Error",
                "Could not send OTP. Check email credentials.\n"
                "The OTP dialog will still open — but you may not receive the code.")

        dialog = OTPDialog(self.email, otp, self)
        if dialog.exec_() == QDialog.Accepted and dialog.verified:
            DB.update_password(self.email, new)          # mirrors Changepassword.change()
            QMessageBox.information(self, "Success", "Your password has been updated successfully!")
            self.cp_current.clear()
            self.cp_new.clear()
            self.cp_confirm.clear()

    # ── Customer Care page (mirrors Bank_Account_main.py com == 4) ────────────
    def _customer_care_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(34, 30, 34, 30)
        layout.setSpacing(20)

        title = QLabel("Customer Care")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(title)

        info = QLabel(
            "Hi there! Need help with your account or have a question?\n"
            "Just type your message below — our Customer Care team is here for you\n"
            "and will respond shortly."
        )
        info.setWordWrap(True)
        info.setStyleSheet("color: #718096; font-size: 13px;")
        layout.addWidget(info)

        msg_card = QGroupBox("Your Message")
        msg_layout = QVBoxLayout()
        msg_layout.setSpacing(12)

        self.care_input = QTextEdit()
        self.care_input.setPlaceholderText("Enter your message here...")
        self.care_input.setMinimumHeight(180)
        msg_layout.addWidget(self.care_input)

        btn_row = QHBoxLayout()
        cancel_btn = warning_btn("Cancel")
        cancel_btn.clicked.connect(self._cancel_care)
        send_btn = primary_btn("Send Message", 44)
        send_btn.clicked.connect(self._handle_care)
        btn_row.addWidget(cancel_btn)
        btn_row.addStretch()
        btn_row.addWidget(send_btn)
        msg_layout.addLayout(btn_row)

        self.care_status = QLabel("")
        self.care_status.setStyleSheet("color: #276749; font-size: 12px;")
        msg_layout.addWidget(self.care_status)

        msg_card.setLayout(msg_layout)
        layout.addWidget(msg_card)
        layout.addStretch()
        page.setLayout(layout)
        return page

    def _cancel_care(self):
        self.care_input.clear()
        self.care_status.setText("Message cancelled.")
        QTimer.singleShot(3000, lambda: self.care_status.setText(""))

    def _handle_care(self):
        """Mirrors Bank_Account_main.py com==4 + customer_message() from Bank_account.py."""
        msg = self.care_input.toPlainText().strip()
        if not msg:
            QMessageBox.warning(self, "Empty Message",
                "Please enter a message before sending.")
            return
        reply = QMessageBox.question(
            self, "Confirm",
            "Do you wish to send this message?\n\n"
            "Our Customer Care team will attend to you shortly.",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                save_customer_message(msg)   # mirrors customer_message()
                self.care_input.clear()
                self.care_status.setText(
                    "Message sent successfully. We will attend to you shortly."
                )
                QTimer.singleShot(6000, lambda: self.care_status.setText(""))
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to send message:\n{str(e)}")
        else:
            self.care_status.setText("Your request to send a message was cancelled.")
            QTimer.singleShot(3000, lambda: self.care_status.setText(""))

    # ── Profile page (account info + password generator) ──────────────────────
    def _profile_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(34, 30, 34, 30)
        layout.setSpacing(20)

        title = QLabel("My Profile")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(title)

        if self.customer:
            # Account info
            info_card = QGroupBox("Account Information")
            form = QFormLayout()
            form.setSpacing(10)
            c = self.customer
            bank_uname = generate_bank_username(c[0])   # from Bank_interface.py
            fields = [
                ("Full Name",      c[0]),
                ("Bank Username",  bank_uname),
                ("Age",            c[1]),
                ("Gender",         c[2]),
                ("Status",         c[3]),
                ("Location",       c[4]),
                ("Phone",          c[5]),
                ("Email",          c[6]),
                ("Account Number", str(c[8])),
            ]
            for label, value in fields:
                lbl = QLabel(str(value))
                lbl.setStyleSheet(
                    "color: #2d3748; font-size: 13px; padding: 3px 0;"
                )
                form.addRow(f"{label}:", lbl)
            info_card.setLayout(form)
            layout.addWidget(info_card)

        # Password generator tool (mirrors Passwordgenerator.generate() from Bank_bulid_1.py)
        gen_card = QGroupBox("Password Generator Tool")
        gen_layout = QVBoxLayout()
        gen_layout.setSpacing(10)

        gen_note = QLabel(
            "Need a strong password? Click the button to generate one.\n"
            "Copy and save it before using it."
        )
        gen_note.setStyleSheet("color: #718096; font-size: 12px;")
        gen_layout.addWidget(gen_note)

        self.gen_output = QLineEdit()
        self.gen_output.setReadOnly(True)
        self.gen_output.setPlaceholderText("Generated password will appear here")
        self.gen_output.setStyleSheet(
            "font-size: 14px; letter-spacing: 2px; padding: 10px; background: #f7fafc;"
        )
        gen_layout.addWidget(self.gen_output)

        gen_btn = success_btn("Generate Strong Password", 44)
        gen_btn.clicked.connect(
            lambda: self.gen_output.setText(generate_strong_password())
        )
        gen_layout.addWidget(gen_btn)
        gen_card.setLayout(gen_layout)
        layout.addWidget(gen_card)

        layout.addStretch()
        page.setLayout(layout)
        return page

    # ── Deposit page ──────────────────────────────────────────────────────────
    def _deposit_page(self):
        page = QWidget()
        layout = QVBoxLayout()
        layout.setContentsMargins(34, 30, 34, 30)
        layout.setSpacing(20)

        title = QLabel("Deposit Money")
        title.setFont(QFont("Arial", 20, QFont.Bold))
        layout.addWidget(title)

        note = QLabel(
            "Enter the amount you wish to deposit into your account.\n"
            "A One-Time Password (OTP) will be sent to your registered email\n"
            "to authorize the deposit before it is processed."
        )
        note.setWordWrap(True)
        note.setStyleSheet("color: #718096; font-size: 12px;")
        layout.addWidget(note)

        form_card = QGroupBox("Deposit Details")
        form = QFormLayout()
        form.setSpacing(14)

        self.dep_amount = QDoubleSpinBox()
        self.dep_amount.setRange(0.01, 9999999.99)
        self.dep_amount.setDecimals(2)
        self.dep_amount.setPrefix("GHS ")
        form.addRow("Deposit Amount:", self.dep_amount)

        form_card.setLayout(form)
        layout.addWidget(form_card)

        dep_btn = success_btn("  Deposit Funds  (sends OTP)", 50)
        dep_btn.clicked.connect(self._handle_deposit)
        layout.addWidget(dep_btn)
        layout.addStretch()
        page.setLayout(layout)
        return page

    def _handle_deposit(self):
        amount = self.dep_amount.value()
        if amount <= 0:
            QMessageBox.warning(self, "Invalid Amount", "Amount must be greater than 0.")
            return

        otp = generate_otp()
        sent = EmailService.send_deposit_otp(self.email, otp, amount)
        if not sent:
            QMessageBox.warning(self, "Email Error",
                "Could not send OTP. Check email credentials.\n"
                "The OTP dialog will still open — but you may not receive the code.")

        dialog = OTPDialog(self.email, otp, self)
        dialog.setWindowTitle("Deposit Authorization — Access Bank")
        if dialog.exec_() == QDialog.Accepted and dialog.verified:
            account_id = str(self.customer[8])
            new_balance, err = DB.deposit(account_id, amount)
            if err:
                QMessageBox.critical(self, "Deposit Failed", err)
                return

            txn_id = generate_transaction_id()
            DB.record_transaction(txn_id, "DEPOSIT", account_id, amount)
            EmailService.send_deposit_confirmation(self.email, amount, txn_id, new_balance)

            self.account = DB.get_account(self.customer[8])
            self._refresh_balance()
            self._refresh_transactions()

            now = datetime.now()
            QMessageBox.information(self, "Deposit Successful",
                f"Your deposit was processed successfully!\n\n"
                f"Amount Deposited : GHS {amount:.2f}\n"
                f"Transaction ID   : {txn_id}\n"
                f"Date & Time      : {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
                f"New Balance      : GHS {new_balance:.2f}\n\n"
                "A confirmation has been sent to your email.")

            self.dep_amount.setValue(0.01)

    # ── Logout (mirrors Bank_Account_main.py com == 5) ────────────────────────
    def _logout(self):
        self.close()
        app = QApplication.instance()
        if hasattr(app, 'auth_window'):
            app.auth_window.show()


# ═══════════════════════════════════════════════════════════════════════════════
#  APPLICATION ENTRY POINT
# ═══════════════════════════════════════════════════════════════════════════════
class AccessBankApp(QApplication):
    def __init__(self):
        super().__init__(sys.argv)
        self.setApplicationName("Access Bank")
        DB.init()
        self.auth_window = AuthWindow()
        self.auth_window.login_success.connect(self._on_login)
        self.auth_window.show()

    def _on_login(self, email: str):
        self.auth_window.hide()
        self.dashboard = Dashboard(email)
        self.dashboard.show()


if __name__ == "__main__":
    app = AccessBankApp()
    sys.exit(app.exec_())
