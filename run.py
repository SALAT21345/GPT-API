from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from g4f.client import Client
import os

from openai import OpenAI

token = os.getenv("OPENROUTER_API_KEY")
if not token:
    print(token)
    raise ValueError("API-ключ не найден в переменных окружения!")


client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key=token,
)
app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешает запросы от всех источников
    allow_credentials=True,
    allow_methods=["*"],  # Разрешает все методы (GET, POST и т.д.)
    allow_headers=["*"],  # Разрешает все заголовки
)

@app.get("/DeepSeek/{prompt}", tags=['Запрос чату гпт_DeepSeek'], summary='DeepSeek')
def DeepSeek_generate_answer_gpt(prompt: str):
    completion = client.chat.completions.create(
    extra_headers={
        "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
        "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
    },
    extra_body={},
    model="deepseek/deepseek-chat",
    messages=[
        {
        "role": "user",
        "content": prompt
        }
    ]
    )
    return(completion.choices[0].message.content)


if __name__ == '__main__':
    app.run(debug=True, port=os.getenv("PORT", default=5000))