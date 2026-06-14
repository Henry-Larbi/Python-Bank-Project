"""
JH Bank - Modern GUI Application
Professional Banking System with PyQt5
Wraps the existing Bank_interface.py and Bank_Account_main.py logic
"""

import sys
import os
import sqlite3
import re
import time
import random
import string
from datetime import datetime
from typing import Optional, Tuple

from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLineEdit, QLabel, QDialog, QMessageBox, QComboBox,
    QTabWidget, QTableWidget, QTableWidgetItem, QSpinBox, QDoubleSpinBox,
    QDateEdit, QTextEdit, QFormLayout, QGroupBox, QProgressBar,
    QStackedWidget, QStatusBar, QMenuBar, QAction, QMenu,
    QTableWidgetSelectionRange, QHeaderView, QListWidget, QListWidgetItem,
    QSplitter, QCheckBox, QRadioButton, QButtonGroup
)
from PyQt5.QtCore import Qt, QDate, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QIcon, QFont, QColor, QPalette, QPixmap
try:
    from PyQt5.QtChart import QChart, QChartView, QBarSeries, QBarSet, QBarCategoryAxis, QValueAxis
    CHARTS_AVAILABLE = True
except ImportError:
    CHARTS_AVAILABLE = False
from PyQt5.QtCore import Qt as QtCore_Qt
import smtplib
from email.message import EmailMessage

# Import the original bank modules
try:
    from Bank_bulid_1 import Register_Identity, check, greet
    from Bank_account import Changepassword, Amount, Transaction, Account, BANK_EMAIL, BANK_EMAIL_PASSWORD
except ImportError as e:
    print(f"Warning: Could not import bank modules: {e}")


class DatabaseManager:
    """Centralized database management"""
    
    DB_FILE = "Bank_JH.db"
    
    @staticmethod
    def init_db():
        """Ensure all required tables exist (safe to call every startup)."""
        conn = sqlite3.connect(DatabaseManager.DB_FILE)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Customer_services(
                Customer_Name TEXT NULL,
                Customer_Age INT,
                Customer_Gender TEXT,
                Customer_Status TEXT,
                Customer_Location TEXT,
                Customer_Phone TEXT,
                Customer_Email TEXT UNIQUE PRIMARY KEY,
                Customer_password TEXT NOT NULL,
                Customer_ID INT UNIQUE
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Account(
                Account_id TEXT PRIMARY KEY,
                Customer_ID INT,
                Current_amount REAL DEFAULT 0,
                Transaction_Date TEXT,
                Transaction_ID TEXT
            )
        ''')

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS Transactions(
                Transaction_ID TEXT PRIMARY KEY,
                From_Account TEXT,
                To_Account TEXT,
                Amount REAL,
                Transaction_Date TEXT,
                Status TEXT
            )
        ''')

        conn.commit()
        conn.close()
    
    @staticmethod
    def get_customer_info(email: str) -> Optional[Tuple]:
        """Get customer information"""
        conn = sqlite3.connect(DatabaseManager.DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Customer_services WHERE Customer_Email = ?', (email,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    @staticmethod
    def get_account_info(customer_id: int) -> Optional[Tuple]:
        """Get account information"""
        conn = sqlite3.connect(DatabaseManager.DB_FILE)
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM Account WHERE Customer_ID = ?', (customer_id,))
        result = cursor.fetchone()
        conn.close()
        return result
    
    @staticmethod
    def get_transactions(account_id: str) -> list:
        """Get transaction history"""
        conn = sqlite3.connect(DatabaseManager.DB_FILE)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM Transactions 
            WHERE From_Account = ? OR To_Account = ?
            ORDER BY Transaction_Date DESC
        ''', (account_id, account_id))
        results = cursor.fetchall()
        conn.close()
        return results


class LoginWindow(QWidget):
    """Login/Sign-up Window"""
    
    login_successful = pyqtSignal(str)  # Signal with email
    
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle("Access Bank - Login")
        self.setGeometry(100, 100, 500, 400)
        self.setStyleSheet(self.get_stylesheet())
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("Access BANK")
        title_font = QFont("Arial", 24, QFont.Bold)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        subtitle = QLabel("Secure Banking Solutions")
        subtitle.setAlignment(Qt.AlignCenter)
        subtitle.setStyleSheet("color: #666; font-size: 12px;")
        layout.addWidget(subtitle)
        
        layout.addSpacing(20)
        
        # Tab widget for login/signup
        tabs = QTabWidget()
        
        # Login Tab
        login_widget = QWidget()
        login_layout = QFormLayout()
        
        self.login_email = QLineEdit()
        self.login_email.setPlaceholderText("Enter your email")
        login_layout.addRow("Email:", self.login_email)
        
        self.login_password = QLineEdit()
        self.login_password.setPlaceholderText("Enter password")
        self.login_password.setEchoMode(QLineEdit.Password)
        login_layout.addRow("Password:", self.login_password)
        
        login_button = QPushButton("Sign In")
        login_button.setStyleSheet(self.get_button_stylesheet())
        login_button.clicked.connect(self.handle_login)
        login_layout.addRow("", login_button)
        
        login_widget.setLayout(login_layout)
        tabs.addTab(login_widget, "Sign In")
        
        # Sign Up Tab
        signup_widget = QWidget()
        signup_layout = QFormLayout()
        
        self.signup_name = QLineEdit()
        self.signup_name.setPlaceholderText("Full name")
        signup_layout.addRow("Full Name:", self.signup_name)
        
        self.signup_age = QSpinBox()
        self.signup_age.setRange(18, 100)
        signup_layout.addRow("Age:", self.signup_age)
        
        self.signup_gender = QComboBox()
        self.signup_gender.addItems(["Male", "Female", "Other"])
        signup_layout.addRow("Gender:", self.signup_gender)
        
        self.signup_status = QComboBox()
        self.signup_status.addItems(["Single", "Married", "Student"])
        signup_layout.addRow("Status:", self.signup_status)
        
        self.signup_location = QLineEdit()
        self.signup_location.setPlaceholderText("Town/City")
        signup_layout.addRow("Location:", self.signup_location)
        
        self.signup_phone = QLineEdit()
        self.signup_phone.setPlaceholderText("Phone number")
        signup_layout.addRow("Phone:", self.signup_phone)
        
        self.signup_email = QLineEdit()
        self.signup_email.setPlaceholderText("Email address")
        signup_layout.addRow("Email:", self.signup_email)
        
        self.signup_password = QLineEdit()
        self.signup_password.setPlaceholderText("8–20 chars, letters, numbers, special chars")
        self.signup_password.setEchoMode(QLineEdit.Password)
        signup_layout.addRow("Password:", self.signup_password)

        self.signup_confirm_password = QLineEdit()
        self.signup_confirm_password.setPlaceholderText("Re-enter password")
        self.signup_confirm_password.setEchoMode(QLineEdit.Password)
        signup_layout.addRow("Confirm Password:", self.signup_confirm_password)

        signup_button = QPushButton("Create Account")
        signup_button.setStyleSheet(self.get_button_stylesheet())
        signup_button.clicked.connect(self.handle_signup)
        signup_layout.addRow("", signup_button)
        
        signup_widget.setLayout(signup_layout)
        tabs.addTab(signup_widget, "Sign Up")
        
        layout.addWidget(tabs)
        
        self.setLayout(layout)
    
    def handle_login(self):
        """Handle login"""
        email = self.login_email.text().strip()
        password = self.login_password.text().strip()
        
        if not email or not password:
            QMessageBox.warning(self, "Input Error", "Please enter email and password")
            return
        
        # Verify credentials
        if check(email, password):
            self.login_successful.emit(email)
            self.login_email.clear()
            self.login_password.clear()
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid email or password")
    
    def handle_signup(self):
        """Handle signup — same validations as Bank_interface.py"""
        from Bank_bulid_1 import Sign_up_check
        import os

        name = self.signup_name.text().strip()
        age = self.signup_age.value()
        gender = self.signup_gender.currentText()
        status = self.signup_status.currentText()
        location = self.signup_location.text().strip()
        phone = self.signup_phone.text().strip()
        email = self.signup_email.text().strip()
        password = self.signup_password.text().strip()
        confirm = self.signup_confirm_password.text().strip()

        if not all([name, phone, email, password, location]):
            QMessageBox.warning(self, "Input Error", "Please fill all required fields")
            return

        # Name: each word must be alphabetic
        name_re = re.compile(r"[a-zA-Z]{3,}")
        for part in name.split():
            if not name_re.match(part):
                QMessageBox.warning(self, "Input Error", "Name must contain only letters, each word at least 3 characters")
                return

        # Phone format: 000-000-0000
        if not re.match(r"^\d{3}-\d{3}-\d{4}$", phone):
            QMessageBox.warning(self, "Input Error", "Phone must follow the format: 050-000-0000")
            return

        # Location: letters only
        if not location.isalpha():
            QMessageBox.warning(self, "Input Error", "Location must contain letters only (no spaces or numbers)")
            return

        # Email
        if not re.match(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,4}", email):
            QMessageBox.warning(self, "Input Error", "Invalid email format")
            return

        # Strong password: 8–20 chars, letters/digits/special chars
        if not re.match(r"[a-zA-Z0-9.!£$%^&*()_+|]{8,20}$", password):
            QMessageBox.warning(self, "Input Error",
                "Password must be 8–20 characters using letters, digits, or special characters (!£$%^&*)")
            return

        if password != confirm:
            QMessageBox.warning(self, "Input Error", "Passwords do not match")
            return

        # Duplicate account check
        if os.path.exists("Bank_JH.db"):
            checker = Sign_up_check(email, password)
            if checker.check():
                QMessageBox.warning(self, "Account Exists", "You already have an account. Please sign in.")
                return

        try:
            customer = Register_Identity(name, age, gender, status, location, phone, email, password)
            if os.path.exists("Bank_JH.db"):
                customer.register()
            else:
                customer.register_not()
            QMessageBox.information(self, "Success", "Account created successfully!\nYou can now sign in.")
            self.signup_name.clear()
            self.signup_email.clear()
            self.signup_password.clear()
            self.signup_confirm_password.clear()
            self.signup_phone.clear()
            self.signup_location.clear()
        except Exception as e:
            QMessageBox.critical(self, "Registration Error", f"Failed to create account: {str(e)}")
    
    @staticmethod
    def get_stylesheet():
        """Get application stylesheet"""
        return """
            QWidget {
                background-color: #f5f5f5;
            }
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #007bff;
                background-color: white;
            }
            QComboBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
            QSpinBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
            QTabWidget::pane {
                border: 1px solid #ddd;
            }
            QTabBar::tab {
                background-color: #e9ecef;
                padding: 8px 20px;
                border: 1px solid #ddd;
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 2px solid #007bff;
            }
        """
    
    @staticmethod
    def get_button_stylesheet():
        """Get button stylesheet"""
        return """
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QPushButton:pressed {
                background-color: #003d82;
            }
        """


class OTPDialog(QDialog):
    """Modal dialog that sends an OTP and asks the user to enter it."""

    def __init__(self, email: str, otp_code: str, parent=None):
        super().__init__(parent)
        self.email = email
        self.otp_code = otp_code
        self.verified = False
        self._init_ui()

    def _init_ui(self):
        self.setWindowTitle("OTP Verification")
        self.setModal(True)
        self.setFixedWidth(380)
        layout = QVBoxLayout()

        info = QLabel(
            f"A One-Time Password has been sent to:\n{self.email}\n\n"
            "Enter the code below to continue.\n"
            "The code expires in 10 minutes."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        self.otp_input = QLineEdit()
        self.otp_input.setPlaceholderText("Enter OTP code")
        self.otp_input.setMaxLength(10)
        layout.addWidget(self.otp_input)

        verify_btn = QPushButton("Verify")
        verify_btn.setStyleSheet(LoginWindow.get_button_stylesheet())
        verify_btn.clicked.connect(self._verify)
        layout.addWidget(verify_btn)

        resend_btn = QPushButton("Resend Code")
        resend_btn.clicked.connect(self._resend)
        layout.addWidget(resend_btn)

        self.setLayout(layout)

    def _verify(self):
        if self.otp_input.text().strip() == self.otp_code:
            self.verified = True
            self.accept()
        else:
            QMessageBox.warning(self, "Incorrect Code", "The OTP you entered is wrong. Try again.")

    def _resend(self):
        sender = Changepassword(self.email, "", self.otp_code)
        sender.confirm_email()
        QMessageBox.information(self, "Code Resent", "A new OTP has been sent to your email.")


class DashboardWindow(QMainWindow):
    """Main Dashboard Window"""
    
    def __init__(self, email: str):
        super().__init__()
        self.email = email
        self.customer_info = DatabaseManager.get_customer_info(email)
        self.account_info = DatabaseManager.get_account_info(self.customer_info[8]) if self.customer_info else None
        self.init_ui()
        self.load_dashboard()
        
    def init_ui(self):
        """Initialize UI"""
        self.setWindowTitle(f"JH Bank Dashboard - {self.email}")
        self.setGeometry(100, 50, 1000, 700)
        self.setStyleSheet(self.get_stylesheet())
        
        # Create menu bar
        self.create_menu_bar()
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout()
        
        # Sidebar
        sidebar = self.create_sidebar()
        layout.addWidget(sidebar, 1)
        
        # Main content area
        self.stacked_widget = QStackedWidget()
        self.stacked_widget.addWidget(self.create_overview_page())
        self.stacked_widget.addWidget(self.create_transactions_page())
        self.stacked_widget.addWidget(self.create_transfer_page())
        self.stacked_widget.addWidget(self.create_settings_page())
        self.stacked_widget.addWidget(self.create_customer_care_page())
        
        layout.addWidget(self.stacked_widget, 4)
        
        central_widget.setLayout(layout)
        
        # Status bar
        self.statusBar().showMessage("Ready")
    
    def create_menu_bar(self):
        """Create menu bar"""
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("File")
        logout_action = QAction("Logout", self)
        logout_action.triggered.connect(self.logout)
        file_menu.addAction(logout_action)
        
        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        help_menu = menubar.addMenu("Help")
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def create_sidebar(self) -> QWidget:
        """Create sidebar"""
        sidebar = QWidget()
        layout = QVBoxLayout()
        
        # Logo/Title
        title = QLabel("JH BANK")
        title_font = QFont("Arial", 16, QFont.Bold)
        title.setFont(title_font)
        layout.addWidget(title)
        
        layout.addSpacing(20)
        
        # Menu buttons
        buttons = [
            ("📊 Overview", 0),
            ("💳 Transactions", 1),
            ("💸 Transfer Money", 2),
            ("⚙️ Settings", 3),
            ("📞 Customer Care", 4),
        ]
        
        for text, page_index in buttons:
            btn = QPushButton(text)
            btn.setMinimumHeight(50)
            btn.clicked.connect(lambda checked, idx=page_index: self.stacked_widget.setCurrentIndex(idx))
            layout.addWidget(btn)
        
        layout.addStretch()
        
        logout_btn = QPushButton("🚪 Logout")
        logout_btn.setMinimumHeight(50)
        logout_btn.setStyleSheet("""
            QPushButton {
                background-color: #dc3545;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c82333;
            }
        """)
        logout_btn.clicked.connect(self.logout)
        layout.addWidget(logout_btn)
        
        sidebar.setLayout(layout)
        sidebar.setStyleSheet("""
            QWidget {
                background-color: #2c3e50;
                color: white;
            }
            QPushButton {
                background-color: #34495e;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 4px;
                text-align: left;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #007bff;
            }
        """)
        
        return sidebar
    
    def create_overview_page(self) -> QWidget:
        """Create overview page"""
        page = QWidget()
        layout = QVBoxLayout()
        
        # Welcome
        welcome = QLabel(f"Welcome, {self.customer_info[0] if self.customer_info else 'Guest'}!")
        welcome_font = QFont("Arial", 18, QFont.Bold)
        welcome.setFont(welcome_font)
        layout.addWidget(welcome)
        
        layout.addSpacing(20)
        
        # Account Summary
        summary_group = QGroupBox("Account Summary")
        summary_layout = QVBoxLayout()
        
        if self.account_info:
            balance = self.account_info[2] if self.account_info[2] else 0
        else:
            balance = 0
        
        balance_label = QLabel(f"Current Balance: GHS {balance:,.2f}")
        balance_font = QFont("Arial", 16, QFont.Bold)
        balance_label.setFont(balance_font)
        balance_label.setStyleSheet("color: #28a745; padding: 10px;")
        summary_layout.addWidget(balance_label)
        
        if self.customer_info:
            account_id = QLabel(f"Account Number: {self.customer_info[8]}")
            account_id.setStyleSheet("padding: 10px;")
            summary_layout.addWidget(account_id)
        
        summary_group.setLayout(summary_layout)
        layout.addWidget(summary_group)
        
        # Quick Actions
        actions_group = QGroupBox("Quick Actions")
        actions_layout = QHBoxLayout()
        
        transfer_btn = QPushButton("Transfer Money")
        transfer_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(2))
        transfer_btn.setMinimumHeight(40)
        actions_layout.addWidget(transfer_btn)
        
        history_btn = QPushButton("View Transactions")
        history_btn.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        history_btn.setMinimumHeight(40)
        actions_layout.addWidget(history_btn)
        
        actions_group.setLayout(actions_layout)
        layout.addWidget(actions_group)
        
        layout.addStretch()
        
        page.setLayout(layout)
        return page
    
    def create_transactions_page(self) -> QWidget:
        """Create transactions page"""
        page = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Transaction History")
        title_font = QFont("Arial", 14, QFont.Bold)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Transactions table
        self.transactions_table = QTableWidget()
        self.transactions_table.setColumnCount(5)
        self.transactions_table.setHorizontalHeaderLabels([
            "Transaction ID", "From Account", "To Account", "Amount", "Date"
        ])
        self.transactions_table.horizontalHeader().setStretchLastSection(True)
        
        layout.addWidget(self.transactions_table)
        
        # Refresh button
        refresh_btn = QPushButton("Refresh")
        refresh_btn.clicked.connect(self.load_transactions)
        layout.addWidget(refresh_btn)
        
        page.setLayout(layout)
        return page
    
    def create_transfer_page(self) -> QWidget:
        """Create transfer page"""
        page = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Transfer Money")
        title_font = QFont("Arial", 14, QFont.Bold)
        title.setFont(title_font)
        layout.addWidget(title)
        
        form_layout = QFormLayout()
        
        self.recipient_account = QLineEdit()
        self.recipient_account.setPlaceholderText("Enter recipient account number")
        form_layout.addRow("Recipient Account:", self.recipient_account)
        
        self.transfer_amount = QDoubleSpinBox()
        self.transfer_amount.setRange(0, 999999.99)
        self.transfer_amount.setDecimals(2)
        form_layout.addRow("Amount (GHS):", self.transfer_amount)
        
        self.transfer_description = QLineEdit()
        self.transfer_description.setPlaceholderText("Description (optional)")
        form_layout.addRow("Description:", self.transfer_description)
        
        layout.addLayout(form_layout)
        
        # Transfer button
        transfer_btn = QPushButton("Send Transfer")
        transfer_btn.setMinimumHeight(40)
        transfer_btn.setStyleSheet(self.get_button_stylesheet())
        transfer_btn.clicked.connect(self.handle_transfer)
        layout.addWidget(transfer_btn)
        
        layout.addStretch()
        
        page.setLayout(layout)
        return page
    
    def create_settings_page(self) -> QWidget:
        """Create settings page"""
        page = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("Account Settings")
        title_font = QFont("Arial", 14, QFont.Bold)
        title.setFont(title_font)
        layout.addWidget(title)
        
        # Change password
        change_pwd_group = QGroupBox("Change Password")
        pwd_layout = QFormLayout()
        
        self.current_password = QLineEdit()
        self.current_password.setEchoMode(QLineEdit.Password)
        pwd_layout.addRow("Current Password:", self.current_password)
        
        self.new_password = QLineEdit()
        self.new_password.setEchoMode(QLineEdit.Password)
        pwd_layout.addRow("New Password:", self.new_password)
        
        self.confirm_password = QLineEdit()
        self.confirm_password.setEchoMode(QLineEdit.Password)
        pwd_layout.addRow("Confirm Password:", self.confirm_password)
        
        change_pwd_btn = QPushButton("Update Password")
        change_pwd_btn.clicked.connect(self.handle_password_change)
        pwd_layout.addRow("", change_pwd_btn)
        
        change_pwd_group.setLayout(pwd_layout)
        layout.addWidget(change_pwd_group)
        
        # Account info
        if self.customer_info:
            info_group = QGroupBox("Account Information")
            info_layout = QVBoxLayout()
            
            info_text = f"""
            Name: {self.customer_info[0]}
            Email: {self.customer_info[6]}
            Phone: {self.customer_info[5]}
            Location: {self.customer_info[4]}
            Account ID: {self.customer_info[8]}
            """
            
            info_label = QLabel(info_text)
            info_label.setStyleSheet("padding: 10px;")
            info_layout.addWidget(info_label)
            
            info_group.setLayout(info_layout)
            layout.addWidget(info_group)
        
        layout.addStretch()
        
        page.setLayout(layout)
        return page
    
    def create_customer_care_page(self) -> QWidget:
        """Customer care page — mirrors the original customer_message() feature."""
        page = QWidget()
        layout = QVBoxLayout()

        title = QLabel("Customer Care")
        title_font = QFont("Arial", 14, QFont.Bold)
        title.setFont(title_font)
        layout.addWidget(title)

        info = QLabel(
            "Hi there! Need help with your account or have a question?\n"
            "Type your message below and our Customer Care team will respond shortly."
        )
        info.setWordWrap(True)
        layout.addWidget(info)

        self.care_message_input = QTextEdit()
        self.care_message_input.setPlaceholderText("Enter your message here...")
        self.care_message_input.setMaximumHeight(150)
        layout.addWidget(self.care_message_input)

        send_btn = QPushButton("Send Message")
        send_btn.setMinimumHeight(40)
        send_btn.setStyleSheet(self.get_button_stylesheet())
        send_btn.clicked.connect(self.handle_customer_care)
        layout.addWidget(send_btn)

        self.care_status_label = QLabel("")
        self.care_status_label.setStyleSheet("color: #28a745; padding: 5px;")
        layout.addWidget(self.care_status_label)

        layout.addStretch()
        page.setLayout(layout)
        return page

    def handle_customer_care(self):
        """Save customer message to docx — same as original customer_message()."""
        from Bank_account import customer_message
        msg = self.care_message_input.toPlainText().strip()
        if not msg:
            QMessageBox.warning(self, "Empty Message", "Please enter a message before sending.")
            return
        reply = QMessageBox.question(
            self, "Confirm", "Do you wish to send this message?",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            try:
                customer_message(msg)
                self.care_message_input.clear()
                self.care_status_label.setText("Message sent successfully. We will attend to you shortly.")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to send message: {str(e)}")
        else:
            self.care_status_label.setText("Message cancelled.")

    def load_dashboard(self):
        """Load dashboard data"""
        self.load_transactions()
    
    def load_transactions(self):
        """Load transaction history"""
        if not self.customer_info:
            return
        
        account_id = str(self.customer_info[8])
        transactions = DatabaseManager.get_transactions(account_id)
        
        self.transactions_table.setRowCount(len(transactions))
        
        for row, transaction in enumerate(transactions):
            for col, value in enumerate(transaction):
                item = QTableWidgetItem(str(value))
                self.transactions_table.setItem(row, col, item)
    
    def handle_transfer(self):
        """Handle money transfer"""
        recipient = self.recipient_account.text().strip()
        amount = self.transfer_amount.value()

        if not recipient or amount <= 0:
            QMessageBox.warning(self, "Input Error", "Please enter a valid account number and amount")
            return

        if not recipient.isdigit() or len(recipient) != 15:
            QMessageBox.warning(self, "Input Error", "Account number must be exactly 15 digits")
            return

        sender_account = str(self.customer_info[8])

        try:
            txn = Transaction(amount, recipient, sender_account)
            if not txn.check():
                QMessageBox.warning(self, "Transfer Failed", "Insufficient funds or sender account not found")
                return

            remaining = txn.send(True)
            txn_id = txn.transaction_generator()
            self._record_transaction(txn_id, sender_account, recipient, amount)
            self._send_transaction_email(amount, recipient, txn_id, remaining)

            QMessageBox.information(
                self, "Transfer Successful",
                f"GHS {amount:.2f} sent to account {recipient}\n"
                f"Transaction ID: {txn_id}\n"
                f"Remaining Balance: GHS {remaining:.2f}\n\n"
                "A confirmation has been sent to your email."
            )
            self.recipient_account.clear()
            self.transfer_amount.setValue(0)
            self.load_transactions()
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Transfer failed: {str(e)}")

    def _record_transaction(self, txn_id, from_account, to_account, amount):
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        conn = sqlite3.connect(DatabaseManager.DB_FILE)
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO Transactions(Transaction_ID,From_Account,To_Account,Amount,Transaction_Date,Status) "
            "VALUES(?,?,?,?,?,?)",
            (str(txn_id), from_account, to_account, amount, now, "Completed")
        )
        conn.commit()
        conn.close()

    def _send_transaction_email(self, amount, recipient, txn_id, remaining):
        server_mail = BANK_EMAIL
        server_password = BANK_EMAIL_PASSWORD
        msg = EmailMessage()
        msg['Subject'] = 'Transaction Confirmation – JH Bank'
        msg['From'] = server_mail
        msg['To'] = self.email
        msg['Reply-To'] = "no-reply@gmail.com"
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        msg.set_content(
            f"Transaction Confirmation\n\n"
            f"Amount Sent : GHS {amount:.2f}\n"
            f"To Account  : {recipient}\n"
            f"Transaction ID : {txn_id}\n"
            f"Date & Time : {now}\n"
            f"Remaining Balance : GHS {remaining:.2f}\n\n"
            "If you did not initiate this transaction, contact support immediately."
        )
        try:
            with smtplib.SMTP("smtp.gmail.com", 587) as server:
                server.ehlo()
                server.starttls()
                server.login(server_mail, server_password)
                server.send_message(msg)
        except Exception:
            pass  # Email failure must not block a completed transfer
    
    @staticmethod
    def _generate_otp() -> str:
        digits = list(range(1, 10))
        return "".join(str(d) for d in random.sample(digits, 6))

    def handle_password_change(self):
        """Handle password change with OTP email verification"""
        current = self.current_password.text()
        new = self.new_password.text()
        confirm = self.confirm_password.text()

        if not all([current, new, confirm]):
            QMessageBox.warning(self, "Input Error", "Please fill all password fields")
            return

        if new != confirm:
            QMessageBox.warning(self, "Input Error", "New passwords do not match")
            return

        if not re.match(r"[A-Za-z0-9!.{}/+\-_]{8,20}$", new):
            QMessageBox.warning(self, "Input Error",
                "Password must be 8–20 characters using letters, digits, or special characters (!.{}/+-_)")
            return

        if not check(self.email, current):
            QMessageBox.warning(self, "Error", "Current password is incorrect")
            return

        # Generate OTP and send to user's email
        otp_code = self._generate_otp()
        changer = Changepassword(self.email, new, otp_code)
        changer.confirm_email()

        # Show OTP dialog — user must verify before the DB is updated
        dialog = OTPDialog(self.email, otp_code, self)
        if dialog.exec_() == QDialog.Accepted and dialog.verified:
            try:
                changer.change()
                QMessageBox.information(self, "Success", "Password changed successfully!")
                self.current_password.clear()
                self.new_password.clear()
                self.confirm_password.clear()
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Failed to update password: {str(e)}")
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.information(self, "About JH Bank",
            "JH Bank v1.0\n\n"
            "Modern Banking Solutions\n\n"
            "© 2024 JH Bank. All rights reserved.")
    
    def logout(self):
        """Logout and return to login"""
        self.close()
        app = QApplication.instance()
        if hasattr(app, 'login_window'):
            app.login_window.show()
    
    @staticmethod
    def get_stylesheet():
        """Get stylesheet"""
        return """
            QMainWindow {
                background-color: #f5f5f5;
            }
            QLineEdit {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #007bff;
            }
            QPushButton {
                background-color: #007bff;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0056b3;
            }
            QGroupBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                margin-top: 10px;
                padding-top: 10px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top left;
                padding: 0 3px;
            }
            QTableWidget {
                border: 1px solid #ddd;
                border-radius: 4px;
                background-color: white;
            }
            QTableWidget::item {
                padding: 5px;
            }
            QDoubleSpinBox {
                border: 1px solid #ddd;
                border-radius: 4px;
                padding: 8px;
                background-color: white;
            }
        """
    
    @staticmethod
    def get_button_stylesheet():
        """Get button stylesheet"""
        return """
            QPushButton {
                background-color: #28a745;
                color: white;
                border: none;
                padding: 10px;
                border-radius: 4px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #218838;
            }
            QPushButton:pressed {
                background-color: #1e7e34;
            }
        """


class MainApp(QApplication):
    """Main Application"""
    
    def __init__(self):
        super().__init__(sys.argv)
        self.setApplicationName("JH Bank")
        
        # Initialize database
        DatabaseManager.init_db()
        
        # Create login window
        self.login_window = LoginWindow()
        self.login_window.login_successful.connect(self.on_login_success)
        self.login_window.show()
    
    def on_login_success(self, email: str):
        """Handle successful login"""
        self.login_window.close()
        self.dashboard = DashboardWindow(email)
        self.dashboard.show()


if __name__ == "__main__":
    app = MainApp()
    sys.exit(app.exec_())
