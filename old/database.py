import sqlite3
from datetime import datetime

DB = "database.db"

# Create Todos Table
def create_todos():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS todos (
            content TEXT,
            created TEXT DEFAULT CURRENT_TIMESTAMP 
        )
    """)
    conn.commit()
    conn.close()


# Query DB for Records
def get_todos():
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("SELECT rowid, * FROM todos")
    rows = c.fetchall()
    conn.close()
    return rows


# Add a New Record
def add_todo(content):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("INSERT INTO todos (content) VALUES (?)", (content,))
    conn.commit()
    conn.close()


# Delete Record
def delete_todo(todo_id):
    conn = sqlite3.connect(DB)
    c = conn.cursor()
    c.execute("DELETE FROM todos WHERE rowid = ?", todo_id)
    conn.commit()
    conn.close()
