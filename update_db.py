import sqlite3

conn = sqlite3.connect("finance.db")
cursor = conn.cursor()

# USERS TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS users(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT
)
""")

# EXPENSE TABLE
cursor.execute("""
CREATE TABLE IF NOT EXISTS expenses(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    category TEXT,
    amount REAL
)
""")

print("Database Updated Successfully")

cursor.execute("""
CREATE TABLE IF NOT EXISTS savings(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    saved_amount REAL
)
""")

print("Savings table created")

cursor.execute("""
CREATE TABLE IF NOT EXISTS learning_progress(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    course_name TEXT,
    completed INTEGER DEFAULT 0,
    points INTEGER DEFAULT 0
)
""")

conn.commit()
conn.close()

print("Learning table created!")