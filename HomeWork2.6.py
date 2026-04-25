import os
import sqlite3
import time
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

# Настройки
BASE_DIR = Path(__file__).resolve().parent
load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")

# База данных
DB = sqlite3.connect("chat_history.db", check_same_thread=False)
DB.execute("CREATE TABLE IF NOT EXISTS messages (id INTEGER PRIMARY KEY AUTOINCREMENT, role TEXT, content TEXT)")
DB.commit()

def save(role, content):
    DB.execute("INSERT INTO messages (role, content) VALUES(?,?)", (role, content))
    DB.commit()

def fetch_history():
    rows = DB.execute("SELECT role, content FROM messages ORDER BY id ASC LIMIT 10").fetchall()
    return "\n".join([f"{'Пользователь' if r=='user' else 'Бот'}: {c}" for r, c in rows]) if rows else "История пуста."

def ask_llm(user_input):
    history = fetch_history()
    
    # Прямая сборка промпта (игнорируем ошибки в файлах, если они есть)
    full_prompt = f"История диалога:\n{history}\n\nНовый вопрос: {user_input}"
    
    try:
        resp = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": "Ты ЗОЖ-коуч. Отвечай на конкретный вопрос пользователя, глядя на историю. Не повторяй приветствия."},
                {"role": "user", "content": full_prompt}
            ],
            temperature=0.7
        )
        return resp.choices[0].message.content.strip()
    except Exception as e:
        return f"Ошибка API: {e}"

def main():
    # Приветствие из файла или стандартное
    try:
        print((BASE_DIR / "welcome.txt").read_text(encoding="utf-8"))
    except:
        print("Привет! Я твой ЗОЖ-бот. О чем пообщаемся?")

    while True:
        try:
            user_msg = input("\nТы: ").strip()
            if not user_msg: continue
            
            if user_msg.lower() == "/delete":
                DB.execute("DELETE FROM messages"); DB.commit()
                print("История очищена!")
                continue

            # СНАЧАЛА СОХРАНЯЕМ
            save("user", user_msg)
            
            print("Бот думает...", end="\r")
            
            # ПОЛУЧАЕМ ОТВЕТ
            answer = ask_llm(user_msg)
            
            print(f"Бот: {answer}")
            save("assistant", answer)
            
        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()