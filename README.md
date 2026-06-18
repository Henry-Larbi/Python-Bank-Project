# Access Bank — Python Banking Application

A full-featured banking system built in Python, available in three forms:
- **Original GUI** — PyQt5 desktop app (the source)
- **Desktop .exe** — standalone Windows executable built with PyInstaller
- **Android APK** — mobile app built with Kivy/KivyMD

All three connect to the same **Supabase cloud PostgreSQL database**, so every user's data is centralised — no local database files needed.

---

## Table of Contents

- [Features](#features)
- [Project Structure](#project-structure)
- [Cloud Database Setup](#cloud-database-setup)
- [Configuration](#configuration)
- [Running the Original GUI](#running-the-original-gui)
- [Building the Desktop .exe](#building-the-desktop-exe)
- [Building the Android APK](#building-the-android-apk)
- [Mobile App Screens](#mobile-app-screens)
- [File Reference](#file-reference)
- [Database Schema](#database-schema)
- [Email Service](#email-service)
- [Security Notes](#security-notes)

---

## Features

| Feature | Desktop GUI | Mobile App |
|---|---|---|
| Account Registration | ✅ | ✅ |
| Login / Authentication | ✅ | ✅ |
| Send Money (Transfer) | ✅ | ✅ |
| View Balance | ✅ | ✅ |
| Transaction History | ✅ | ✅ |
| Change Password (OTP) | ✅ | ✅ |
| Loans | ✅ | — |
| Fixed Deposits | ✅ | — |
| Bill Payments | ✅ | — |
| Recurring Payments | ✅ | — |
| Notifications | ✅ | — |
| Admin Dashboard | ✅ | — |
| Fraud Detection | ✅ | — |
| Welcome Email | ✅ | ✅ |
| Transaction Confirmation Email | ✅ | ✅ |
| Password Generator | ✅ | ✅ |

---

## Project Structure

```
Python-Bank-Project/
│
├── final_main_gui_bank.py      # ★ Original PyQt5 GUI (untouched source)
├── AccessBank_desktop.py       # Copy of above — used for .exe builds
│
├── AccessBank.spec             # PyInstaller config → builds AccessBank.exe
├── build.bat                   # Windows: double-click to build .exe
├── build.sh                    # Mac/Linux: run to build executable
│
├── mobile/                     # Android APK (Kivy/KivyMD)
│   ├── main.py                 # App entry point
│   ├── buildozer.spec          # Android build config
│   ├── requirements.txt        # Mobile dependencies
│   └── screens/
│       ├── login.py
│       ├── register.py
│       ├── dashboard.py
│       ├── send_money.py
│       ├── transactions.py
│       └── change_password.py
│
├── db.py                       # Shared cloud database functions (psycopg2)
├── config.py                   # ★ Supabase URL + email credentials (edit this)
├── email_service.py            # Email module (OTP, notifications, welcome)
│
├── Bank_account.py             # Core banking logic module
├── Bank_Account_main.py        # CLI dashboard
├── Bank_bulid_1.py             # Core registration & login logic
│
└── requirements.txt            # Desktop dependencies
```

---

## Cloud Database Setup

This project uses **Supabase** (hosted PostgreSQL) as its central database. All users — whether on the desktop app, `.exe`, or Android APK — connect to the same database.

### Step 1 — Create a Supabase project

1. Go to [supabase.com](https://supabase.com) and sign up (free)
2. Click **New Project**, give it a name, set a password, choose a region
3. Wait ~2 minutes for the project to initialise

### Step 2 — Get your connection string

1. In your project → **Settings** → **Database** → **Connection string** → **URI**
2. Copy the string — it looks like:
   ```
   postgresql://postgres:<password>@db.<project-ref>.supabase.co:5432/postgres
   ```

### Step 3 — Create the tables

Go to **SQL Editor** in your Supabase dashboard and run:

```sql
CREATE TABLE IF NOT EXISTS Customer_services (
    Customer_Name     TEXT NOT NULL,
    Customer_Age      TEXT NOT NULL,
    Customer_Gender   TEXT NOT NULL,
    Customer_Status   TEXT NOT NULL,
    Customer_Location TEXT NOT NULL,
    Customer_Phone    TEXT NOT NULL,
    Customer_Email    TEXT NOT NULL UNIQUE PRIMARY KEY,
    Customer_password TEXT NOT NULL,
    Customer_ID       INTEGER NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS Account (
    Account_id       TEXT PRIMARY KEY,
    Customer_ID      INTEGER,
    Current_amount   REAL DEFAULT 0,
    Transaction_Date TEXT,
    Transaction_ID   TEXT
);

CREATE TABLE IF NOT EXISTS Transactions (
    Transaction_ID   TEXT PRIMARY KEY,
    From_Account     TEXT,
    To_Account       TEXT,
    Amount           REAL,
    Transaction_Date TEXT,
    Status           TEXT
);

CREATE TABLE IF NOT EXISTS Loans (
    Loan_ID         TEXT PRIMARY KEY,
    Account_ID      TEXT,
    Amount          REAL,
    Interest_Rate   REAL,
    Months          INTEGER,
    Monthly_Payment REAL,
    Start_Date      TEXT,
    Status          TEXT DEFAULT 'Active',
    Amount_Repaid   REAL DEFAULT 0
);

CREATE TABLE IF NOT EXISTS FixedDeposits (
    FD_ID           TEXT PRIMARY KEY,
    Account_ID      TEXT,
    Amount          REAL,
    Interest_Rate   REAL,
    Days            INTEGER,
    Start_Date      TEXT,
    Maturity_Date   TEXT,
    Expected_Return REAL,
    Status          TEXT DEFAULT 'Active'
);

CREATE TABLE IF NOT EXISTS BillPayments (
    Payment_ID   TEXT PRIMARY KEY,
    Account_ID   TEXT,
    Biller       TEXT,
    Amount       REAL,
    Payment_Date TEXT,
    Status       TEXT DEFAULT 'Paid'
);

CREATE TABLE IF NOT EXISTS RecurringPayments (
    Schedule_ID   TEXT PRIMARY KEY,
    Account_ID    TEXT,
    Recipient_ID  TEXT,
    Amount        REAL,
    Frequency     TEXT,
    Next_Run_Date TEXT,
    Status        TEXT DEFAULT 'Active',
    Description   TEXT
);

CREATE TABLE IF NOT EXISTS Notifications (
    Notif_ID     TEXT PRIMARY KEY,
    Account_ID   TEXT,
    Message      TEXT,
    Type         TEXT,
    Created_Date TEXT,
    Is_Read      INTEGER DEFAULT 0
);

CREATE TABLE IF NOT EXISTS FrozenAccounts (
    Account_ID  TEXT PRIMARY KEY,
    Frozen_Date TEXT,
    Reason      TEXT
);
```

---

## Configuration

Open `config.py` and fill in your credentials:

```python
# Supabase PostgreSQL connection string (from Step 2 above)
DATABASE_URL = "postgresql://postgres:<password>@db.<project-ref>.supabase.co:5432/postgres"

# Gmail address used to send OTPs and notifications
BANK_EMAIL = "your@gmail.com"

# Gmail App Password (not your regular password)
# Get it from: Google Account → Security → 2-Step Verification → App passwords
BANK_EMAIL_PASSWORD = "xxxx xxxx xxxx xxxx"

# Admin panel credentials
ADMIN_EMAIL    = "admin"
ADMIN_PASSWORD = "admin1"
```

> `config.py` is the only file you need to edit. All three app versions read from it.

---

## Running the Original GUI

```bash
# Install dependencies
pip install -r requirements.txt

# Run
python final_main_gui_bank.py
```

**Requirements:** Python 3.8+, PyQt5, psycopg2-binary, python-docx

---

## Building the Desktop .exe

The `.exe` bundles everything — PyQt5, psycopg2, config, and all logic — into a single file. No Python installation needed on the target machine.

**On Windows — double-click `build.bat`**

**On Mac/Linux:**
```bash
chmod +x build.sh
./build.sh
```

The finished executable appears at `dist/AccessBank.exe` (Windows) or `dist/AccessBank` (Mac/Linux).

> Build the `.exe` on Windows if your users are on Windows. The output platform matches the build machine.

**Files to share with others:**
```
dist/AccessBank.exe   ← the only file they need
```

---

## Building the Android APK

The mobile app is built with Kivy and KivyMD. Building requires **Linux** (use WSL on Windows).

```bash
# Install Buildozer
pip install buildozer

# Build the APK (first build takes 15–30 min — downloads Android SDK/NDK)
cd mobile
buildozer android debug
```

The APK appears at `mobile/bin/AccessBank-1.0-debug.apk`.

**Test on your computer first (before building APK):**
```bash
cd mobile
pip install -r requirements.txt
python main.py
```

---

## Mobile App Screens

| Screen | Features |
|---|---|
| Login | Email + password, connects to Supabase |
| Register | Full validation, auto-generates 15-digit account number |
| Dashboard | Balance card, account number, quick action buttons |
| Send Money | Transfer funds with balance check and receipt |
| Transactions | Full history with sent/received labels |
| Change Password | OTP sent to email → update password |

---

## File Reference

### `config.py`
Central configuration file. Contains the Supabase connection URL, Gmail credentials, and admin login. **This is the only file you need to edit** to connect the app to your database.

### `db.py`
Shared database module used by all three app versions. Provides functions:

| Function | Description |
|---|---|
| `get_connection()` | Opens a psycopg2 connection to Supabase |
| `init_tables()` | Creates all tables if they don't exist |
| `login(email, password)` | Validates credentials |
| `register(...)` | Creates a new customer and account |
| `is_duplicate(email)` | Checks if email is already registered |
| `get_customer(email)` | Fetches customer row |
| `get_account(customer_id)` | Fetches account row |
| `get_transactions(account_id)` | Returns full transaction history |
| `transfer(sender, recipient, amount)` | Atomic debit/credit transfer |
| `record_transaction(...)` | Saves transaction to DB |
| `update_password(email, new_password)` | Updates customer password |

### `final_main_gui_bank.py`
The original self-contained PyQt5 desktop application. All database operations, email logic, validation, and UI are in one file. Kept as the untouched source of truth.

### `AccessBank_desktop.py`
An exact copy of `final_main_gui_bank.py` used as the entry point for PyInstaller builds. Keeping it separate ensures the original is never altered during the build process.

### `AccessBank.spec`
PyInstaller build configuration. Specifies `AccessBank_desktop.py` as the entry point, includes all hidden imports (psycopg2, PyQt5), and sets `console=False` for a clean GUI-only window.

### `build.bat` / `build.sh`
One-click build scripts. Install all dependencies and run PyInstaller automatically.

### `mobile/main.py`
Kivy/KivyMD application entry point. Initialises the screen manager and registers all screens. Reads `config.py` and `db.py` from the parent directory.

### `mobile/buildozer.spec`
Android build configuration. Targets API 33, supports ARM64 and ARMv7, requests `INTERNET` permission for the Supabase connection.

### `email_service.py`
Standalone email module. Imports credentials from `config.py`.

| Function | Purpose |
|---|---|
| `send_otp(to, code)` | Sends a 6-digit password reset OTP |
| `send_transaction_confirmation(...)` | Sends transfer receipt to sender |
| `send_welcome(to, name, account_id, username)` | Sends account details on registration |

### `Bank_account.py`
Core banking logic used by the CLI and modular builds. Updated to use `db.py` and `config.py`.

### `Bank_bulid_1.py`
Core registration and login logic used by the CLI. Updated to use `db.py` and `config.py`.

### `Bank_Account_main.py`
CLI dashboard. Launched with a user's email as a command-line argument:
```bash
python Bank_Account_main.py user@example.com
```

---

## Database Schema

The database has 9 tables hosted on Supabase PostgreSQL:

| Table | Purpose |
|---|---|
| `Customer_services` | Customer profiles and login credentials |
| `Account` | Account balances and transaction references |
| `Transactions` | Full transfer history |
| `Loans` | Loan records with repayment tracking |
| `FixedDeposits` | Fixed deposit investments |
| `BillPayments` | Utility and bill payment records |
| `RecurringPayments` | Standing orders / scheduled transfers |
| `Notifications` | In-app notification feed |
| `FrozenAccounts` | Admin-frozen account records |

---

## Email Service

All emails are sent from the configured Gmail account via **SMTP_SSL (port 465)**:

1. **Welcome Email** — sent on successful registration with account number and username
2. **OTP / Password Reset** — 6-digit one-time code, valid for 10 minutes
3. **Transaction Confirmation** — sent to sender after every successful transfer

> Gmail requires **2-Step Verification** enabled and an **App Password** (not your regular Gmail password) set in `config.py`.

---

## Security Notes

- Passwords are stored as plain text. For a production system, replace with `bcrypt` hashing.
- The `Bank_JH.db` local database file is gitignored and no longer used — all data lives in Supabase.
- `config.py` contains sensitive credentials. Do not commit it to a public repository without replacing the real values with placeholders.
- OTP codes are single-use and expire in 10 minutes (enforced by messaging — no server-side timer).
- Account numbers are 15-digit randomly generated integers, unique per customer.
- The admin panel is accessible only from the desktop GUI using the credentials in `config.py`.
