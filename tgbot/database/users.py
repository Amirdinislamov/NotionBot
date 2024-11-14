import sqlite3

def init_users_db():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            notion_token TEXT,
            notion_database_id TEXT
        )
    """)
    conn.commit()
    conn.close()

def save_user_token(user_id, token, database_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
        INSERT OR REPLACE INTO users (user_id, notion_token, notion_database_id)
        VALUES (?, ?, ?)
    """, (user_id, token, database_id))
    conn.commit()
    conn.close()

def get_user_token(user_id):
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("SELECT notion_token, notion_database_id FROM users WHERE user_id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result if result else (None, None)

init_users_db()
