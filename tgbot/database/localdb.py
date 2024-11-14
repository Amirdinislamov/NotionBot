import sqlite3
import os

db_path = os.path.join(os.path.dirname(__file__), "links.db")

def initialize_database():
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
                CREATE TABLE IF NOT EXISTS links (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    url TEXT NOT NULL,
                    title TEXT,
                    category TEXT,
                    priority INTEGER,
                    source TEXT,
                    telegram_user_id INTEGER
                )
            """)
        conn.commit()

def add_link(url: str, title: str, category: str, priority: int, source: str, telegram_user_id: int):
    with sqlite3.connect(db_path) as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO links (url, title, category, priority, source, telegram_user_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (url, title, category, priority, source, telegram_user_id))
        conn.commit()
        print("Запись добавлена успешно!")

        # Проверка записей после добавления
        cursor.execute("SELECT * FROM links")
        rows = cursor.fetchall()
        print("Содержимое таблицы links после добавления записи:", rows)




