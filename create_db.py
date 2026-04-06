import sqlite3

conn = sqlite3.connect("finance.db")
cursor = conn.cursor()

# USERS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY AUTOINCREMENT,
username TEXT UNIQUE,
password TEXT
)
""")

# EXPENSE TABLE (WITH user_id ✅)
cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
category TEXT,
amount REAL
)
""")

print("Database Ready Successfully")

conn.commit()
conn.close()