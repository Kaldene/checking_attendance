# database.py
import sqlite3

conn = sqlite3.connect("database/student.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
    CREATE TABLE IF NOT EXISTS student (
        name TEXT NOT NULL,
        age INTEGER NOT NULL,
        email TEXT UNIQUE,
        created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
    )
""")

user_data = [
    ("Мария Сидорова", 25, "maria@example.com"),
    ("Петр Иванов", 35, "petr@example.com"),
    ("Анна Козлова", 28, "anna@example.com")
]

# Используем INSERT OR IGNORE, чтобы избежать дубликатов
cursor.executemany(
    """INSERT OR IGNORE INTO student (name, age, email) VALUES (?, ?, ?)""", user_data
)

conn.commit()
conn.close()
print("Данные успешно обработаны (дубликаты пропущены).")