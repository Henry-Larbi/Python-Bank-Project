# Access Bank — Python Banking Application

A full-featured banking system built in Python, offering both a command-line interface (CLI) and a modern graphical user interface (GUI) powered by PyQt5. The application covers account registration, authentication, fund transfers, OTP-secured password changes, transaction history, and customer care — all backed by a local SQLite database.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Architecture Overview](#architecture-overview)
- [Requirements](#requirements)
- [Installation](#installation)
- [Running the Application](#running-the-application)
- [File Reference](#file-reference)
- [Database Schema](#database-schema)
- [Email Service](#email-service)
- [Security Notes](#security-notes)

---

## Features

| Feature | CLI | GUI |
|---|---|---|
| Account Registration | ✅ | ✅ |
| Login / Authentication | ✅ | ✅ |
| Send Money (Transfer) | ✅ | ✅ |
| View Balance | ✅ | ✅ |
| Transaction History | ✅ | ✅ |
| Change Password (OTP-verified) | ✅ | ✅ |
| Customer Care Messaging | ✅ | ✅ |
| Password Generator | ✅ | ✅ |
| Welcome Email on Sign-up | ✅ | ✅ |
| Transaction Confirmation Email | ✅ | ✅ |
| OTP Email Verification | ✅ | ✅ |

---

## Project Structure

```
Python-Bank-Project/
│
├── final_main_gui_bank.py      # ★ Main entry point — standalone GUI (recommended)
│
├── bank_gui_main.py            # Alternative GUI (imports from other modules)
│
├── Bank_interface.py           # CLI — registration & sign-in interface
├── Bank_Account_main.py        # CLI — dashboard (transfer, password, care, logout)
│
├── Bank_bulid_1.py             # Core: registration logic, login check, email, password gen
├── Bank_account.py             # Core: transactions, amount checks, password change, reports
│
├── email_service.py            # Standalone email module (can be run & imported separately)
│
├── Bank_JH.db                  # SQLite database (auto-created on first run)
├── Bank_JH.txt                 # Text backup of registered customer credentials (append)
├── Bank_Transaction.txt        # Text log of all transactions (append)
└── Bank_customer_report.docx   # Customer care messages (auto-created, requires python-docx)
```

---

## Architecture Overview

The project is organised in two layers:

### Core Layer (shared logic)

```
Bank_bulid_1.py
  ├── Register_Identity   — creates accounts, writes to DB and Bank_JH.txt
  ├── Sign_up_check       — prevents duplicate email registration
  ├── check()             — validates login credentials against DB
  ├── send_email          — sends welcome emails via SMTP
  └── Passwordgenerator   — generates strong random passwords

Bank_account.py
  ├── Amount              — reads current account balance from DB
  ├── Transaction         — checks funds, deducts sender, credits recipient, logs to DB
  ├── Changepassword      — sends OTP email, updates password in DB
  ├── customer_message()  — appends customer care messages to .docx report
  └── get_account_number()— retrieves account number and balance by email
```

### Interface Layer (CLI and GUI)

```
CLI path:
  Bank_interface.py  →  Bank_Account_main.py
       ↓                        ↓
  (Registration &          (Dashboard: transfer,
   Sign-in)                 password change, care)

GUI path (integrated):
  final_main_gui_bank.py  (self-contained — no imports from other project files)
       ├── DB class         — all database operations
       ├── EmailService     — OTP, transaction, and welcome emails
       ├── AuthWindow       — Login + Registration (tabbed, resizable)
       ├── OTPDialog        — modal OTP verification dialog
       └── Dashboard        — 6-page sidebar navigation
             ├── Overview          (balance card + quick actions)
             ├── Send Money        (transfer with email confirmation)
             ├── Transaction History (full log table)
             ├── Change Password   (OTP-secured)
             ├── Customer Care     (sends message to .docx report)
             └── My Profile        (account info + password generator)

GUI path (modular):
  bank_gui_main.py  →  imports Bank_bulid_1, Bank_account
```

---

## Requirements

- Python 3.8 or higher
- PyQt5
- python-docx *(optional — required only for Customer Care message saving)*

Install all dependencies:

```bash
pip install PyQt5 python-docx
```

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/henry-larbi/python-bank-project.git
cd python-bank-project

# 2. Install dependencies
pip install PyQt5 python-docx

# 3. Run the application
python final_main_gui_bank.py
```

The SQLite database (`Bank_JH.db`) and all required tables are created automatically on first launch — no setup required.

---

## Running the Application

### Recommended — Integrated GUI (single file, no dependencies on other project files)

```bash
python final_main_gui_bank.py
```

### Alternative GUI (modular, imports from core files)

```bash
python bank_gui_main.py
```

### CLI — Registration & Sign-in

```bash
python Bank_interface.py
```

### CLI — Dashboard (requires a logged-in email passed as an argument)

```bash
python Bank_Account_main.py your@email.com
```

### Email Service (standalone test / import)

```bash
python email_service.py
```

Or import it in any script:

```python
from email_service import send_otp, send_transaction_confirmation, send_welcome
```

---

## File Reference

### `final_main_gui_bank.py`
The recommended entry point. A fully self-contained PyQt5 application — all database operations, email logic, validation, and UI are embedded in a single file. No imports from other project files are needed.

**Key classes:**

| Class | Responsibility |
|---|---|
| `DB` | All SQLite operations (init tables, register, login, transfer, history) |
| `EmailService` | Sends OTP, transaction confirmation, and welcome emails via SMTP_SSL |
| `AuthWindow` | Tabbed login / registration window with full field validation |
| `OTPDialog` | Modal dialog for entering and verifying a one-time password |
| `Dashboard` | Main window with sidebar navigation across 6 feature pages |
| `AccessBankApp` | Application entry point; initialises DB and shows AuthWindow |

---

### `bank_gui_main.py`
An alternative GUI that imports `Bank_bulid_1` and `Bank_account` for its logic. Functionally equivalent to `final_main_gui_bank.py` but relies on the other project files being present.

---

### `Bank_bulid_1.py`
Core infrastructure module.

- `Register_Identity` — validates and stores a new customer in `Customer_services` and creates their `Account` row with a 15-digit account number.
- `Sign_up_check` — queries the DB to prevent duplicate email registrations.
- `check(email, password)` — returns `True` if credentials match the DB record.
- `send_email` — sends a welcome email using `smtplib`.
- `Passwordgenerator.generate()` — returns a random 10-character strong password (uppercase, lowercase, digits, symbols).

---

### `Bank_account.py`
Core account operations module.

- `Amount.check_amount()` — fetches current balance for an account ID.
- `Transaction` — handles the full transfer flow: balance check on the sender, atomic debit/credit, transaction ID generation, text report, and DB record.
- `Changepassword` — sends an OTP email and updates the password in `Customer_services`.
- `customer_message(msg)` — appends a customer care message to `Bank_customer_report.docx`.
- `get_account_number(email)` — retrieves the account number and balance for a given email.

---

### `Bank_interface.py`
CLI entry point for registration and sign-in. Validates all input (name format, phone pattern `050-000-0000`, email regex, strong password, status) before calling `Register_Identity.register()` or `Register_Identity.register_not()` depending on whether the database already exists.

---

### `Bank_Account_main.py`
CLI dashboard launched after login. Accepts the user's email as a command-line argument.

| Option | Action |
|---|---|
| 1 | Send Money — validates recipient account (15 digits), checks balance, transfers funds |
| 2 | Change Password — sends OTP, verifies code, updates password |
| 3 | View Transactions *(placeholder)* |
| 4 | Customer Care — sends a message to the `.docx` report |
| 5 | Logout |

---

### `email_service.py`
Standalone module containing all email-sending functions. Can be imported by any script or executed directly to test email delivery.

| Function | Purpose |
|---|---|
| `send_otp(to_email, otp_code)` | Sends a 6-digit password reset code |
| `send_transaction_confirmation(...)` | Sends transfer details after a successful payment |
| `send_welcome(to_email, name, account_id, username)` | Sends account credentials on registration |

Uses `smtplib.SMTP_SSL` on port **465** with `msg.encode("utf-8")` to support all characters.

---

## Database Schema

**`Customer_services`**

| Column | Type | Description |
|---|---|---|
| Customer_Name | TEXT | Full name |
| Customer_Age | TEXT | Age |
| Customer_Gender | TEXT | Male / Female |
| Customer_Status | TEXT | Single / Married / Student |
| Customer_Location | TEXT | Town or city |
| Customer_Phone | TEXT | Format: 050-000-0000 |
| Customer_Email | TEXT (PK) | Unique login identifier |
| Customer_password | TEXT | Plain-text password |
| Customer_ID | INT (UNIQUE) | 15-digit auto-generated account number |

**`Account`**

| Column | Type | Description |
|---|---|---|
| Account_id | TEXT (PK) | String form of Customer_ID |
| Customer_ID | INT | Foreign key to Customer_services |
| Current_amount | REAL | Running balance (default 0.0) |
| Transaction_Date | TEXT | Date of last transaction |
| Transaction_ID | TEXT | ID of last transaction |

**`Transactions`**

| Column | Type | Description |
|---|---|---|
| Transaction_ID | TEXT (PK) | 9-digit unique transaction reference |
| From_Account | TEXT | Sender's account ID |
| To_Account | TEXT | Recipient's account ID |
| Amount | REAL | Amount transferred (GHS) |
| Transaction_Date | TEXT | Timestamp of transaction |
| Status | TEXT | e.g. "Completed" |

---

## Email Service

Outgoing emails are sent from the bank's Gmail account using **SMTP_SSL on port 465**. Three email types are supported:

1. **Welcome Email** — sent on successful registration with account credentials.
2. **OTP / Password Reset** — a 6-digit one-time code valid for 10 minutes, sent before any password change.
3. **Transaction Confirmation** — sent to the sender after every successful transfer, showing amount, recipient, transaction ID, and remaining balance.

The bank email credentials are defined as constants in `final_main_gui_bank.py` (`BANK_EMAIL`, `BANK_EMAIL_PASSWORD`) and in `Bank_account.py` for the modular files.

> **Gmail requirement:** The account must have **2-Step Verification** enabled and use an **App Password** (not the regular account password) in `BANK_EMAIL_PASSWORD`.

---

## Security Notes

- Passwords are stored as plain text in the current implementation. For production use, replace with `bcrypt` or `hashlib` hashing.
- The bank email app password is stored directly in source files. For production, move credentials to environment variables or a secrets manager.
- OTP codes are valid for 10 minutes (enforced by messaging only — no server-side expiry timer in the current version).
- Account numbers are 15-digit randomly sampled integers, unique per customer.
