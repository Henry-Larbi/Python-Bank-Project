import sqlite3 as sql
connection = sql.connect("Bank_JH.db")
cursor = connection.cursor()
cursor.execute("SELECT * FROM   ")