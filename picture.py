import os
import base64
import pathlib
from io import BytesIO
from PIL import Image
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

MODEL = "dall-e-3"

def save_png_from_b64(b64_str, path):
    img_bytes = base64.b64decode(b64_str)
    Image.open(BytesIO(img_bytes)).save(path, format="PNG")

def main():
    user_prompt = input("Введите описание для генерации (Prompt): ")
    
    out_dir = pathlib.Path("images")
    out_dir.mkdir(exist_ok=True)
    out_path = out_dir / "generated-image1.png"

    try:
        resp = client.images.generate(
            model=MODEL,
            prompt=user_prompt,
            size="1024x1024",
            n=1,
            response_format="b64_json"
        )

        b64_data = resp.data[0].b64_json
        
        if b64_data:
            save_png_from_b64(b64_data, out_path)
            
            # Вывод информации в консоль
            print(f"\nИспользованный промпт: {user_prompt}")
            print(f"Путь к сохранённому файлу: {out_path.resolve()}")
            
            Image.open(out_path).show()
        else:
            print("Ошибка: Данные b64 не получены.")

    except Exception as e:
        print(f"Ошибка: {repr(e)}")

if __name__ == "__main__":
    main()