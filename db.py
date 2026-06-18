import psycopg2
import config


def get_connection():
    return psycopg2.connect(config.DATABASE_URL)


def init_tables():
    conn = get_connection()
    cur  = conn.cursor()
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
            Customer_ID       INTEGER NOT NULL UNIQUE
        )''')
    cur.execute('''
        CREATE TABLE IF NOT EXISTS Account(
            Account_id       TEXT PRIMARY KEY,
            Customer_ID      INTEGER,
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


def get_customer(email):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM Customer_services WHERE Customer_Email = %s", (email,))
    row  = cur.fetchone()
    conn.close()
    return row


def get_account(customer_id):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT * FROM Account WHERE Customer_ID = %s", (customer_id,))
    row  = cur.fetchone()
    conn.close()
    return row


def get_transactions(account_id):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute('''
        SELECT * FROM Transactions
        WHERE From_Account = %s OR To_Account = %s
        ORDER BY Transaction_Date DESC
    ''', (str(account_id), str(account_id)))
    rows = cur.fetchall()
    conn.close()
    return rows


def login(email, password):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT Customer_password FROM Customer_services WHERE Customer_Email = %s", (email,))
    data = cur.fetchone()
    conn.close()
    return data is not None and password == data[0]


def is_duplicate(email):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT Customer_Email FROM Customer_services WHERE Customer_Email = %s", (email,))
    result = cur.fetchone()
    conn.close()
    return result is not None


def register(name, age, gender, status, location, phone, email, password, account_id):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute('''
        INSERT INTO Customer_services(
            Customer_Name, Customer_Age, Customer_Gender, Customer_Status,
            Customer_Location, Customer_Phone, Customer_Email,
            Customer_password, Customer_ID)
        VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)
    ''', (name, str(age), gender, status, location, phone, email, password, account_id))
    cur.execute('''
        INSERT INTO Account(Account_id, Customer_ID, Current_amount, Transaction_Date, Transaction_ID)
        VALUES(%s,%s,%s,%s,%s)
    ''', (str(account_id), account_id, 0.0, None, None))
    conn.commit()
    conn.close()


def update_password(email, new_password):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute(
        "UPDATE Customer_services SET Customer_password = %s WHERE Customer_Email = %s",
        (new_password, email)
    )
    conn.commit()
    conn.close()


def transfer(sender_id, recipient_id, amount):
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute("SELECT Current_amount FROM Account WHERE Account_id = %s", (str(sender_id),))
    row = cur.fetchone()
    if row is None:
        conn.close()
        return None, "Sender account not found."
    if float(row[0]) < amount:
        conn.close()
        return None, "Insufficient funds. Please recharge!"
    cur.execute("SELECT Account_id FROM Account WHERE Account_id = %s", (str(recipient_id),))
    if cur.fetchone() is None:
        conn.close()
        return None, "Recipient account not found."
    cur.execute(
        "UPDATE Account SET Current_amount = Current_amount - %s WHERE Account_id = %s",
        (amount, str(sender_id))
    )
    cur.execute(
        "UPDATE Account SET Current_amount = Current_amount + %s WHERE Account_id = %s",
        (amount, str(recipient_id))
    )
    cur.execute("SELECT Current_amount FROM Account WHERE Account_id = %s", (str(sender_id),))
    new_balance = cur.fetchone()[0]
    conn.commit()
    conn.close()
    return new_balance, None


def record_transaction(txn_id, from_account, to_account, amount):
    from datetime import datetime
    now  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_connection()
    cur  = conn.cursor()
    cur.execute('''
        INSERT INTO Transactions(Transaction_ID, From_Account, To_Account, Amount, Transaction_Date, Status)
        VALUES(%s,%s,%s,%s,%s,%s)
    ''', (str(txn_id), str(from_account), str(to_account), amount, now, "Completed"))
    conn.commit()
    conn.close()
