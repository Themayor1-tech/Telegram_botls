import sqlite3

conn = sqlite3.connect("safe_group_ai.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS groups (
    chat_id INTEGER PRIMARY KEY,
    premium INTEGER DEFAULT 0,
    trial_start INTEGER
)
""")
conn.commit()

def add_group(chat_id, trial_start):
    cursor.execute(
        "INSERT OR IGNORE INTO groups (chat_id, trial_start) VALUES (?, ?)",
        (chat_id, trial_start)
    )
    conn.commit()

def set_premium(chat_id):
    cursor.execute(
        "UPDATE groups SET premium=1 WHERE chat_id=?",
        (chat_id,)
    )
    conn.commit()

def is_premium(chat_id):
    cursor.execute(
        "SELECT premium FROM groups WHERE chat_id=?",
        (chat_id,)
    )
    row = cursor.fetchone()
    return row and row[0] == 1
