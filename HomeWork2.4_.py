import sqlite3
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

# Инициализация клиента OpenAI
client = OpenAI(api_key=os.getenv("OPENAI_BASE_API_KEY"))

# Создаем или подключаемся к базе SQLite
db = sqlite3.connect("chat.db")
db.execute("CREATE TABLE IF NOT EXISTS messages(id INTEGER PRIMARY KEY, role TEXT, content TEXT)")
db.commit()

# Функция для добавления сообщений в базу
def add(role, txt):
    db.execute("INSERT INTO messages(role, content) VALUES(?, ?)", (role, txt))
    db.commit()

# Функция для получения всех сообщений из базы в формате OpenAI
def msgs():
    return [{"role": r, "content": c} for r, c in db.execute("SELECT role, content FROM messages ORDER BY id")]

# Мини-чат
print("Мини-чат (OpenAI + SQLite). Ctrl+C для выхода.")
while True:
    try:
        q = input("Ты: ").strip()
    except KeyboardInterrupt:
        print("\nПока!")
        break

    if not q:
        continue

    add("user", q)

    # Запрос к OpenAI
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # или нужная тебе модель
        messages=msgs()
    )

    reply = response.choices[0].message.content
    add("assistant", reply)
    print("Бот:", reply, "\n")