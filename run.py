from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
# import uvicorn
from g4f.client import Client
import os
# import asyncio
from openai import OpenAI
token = "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"
# Фикс для Windows (если используешь Windows)
# if asyncio.get_event_loop_policy().__class__.__name__ != "WindowsSelectorEventLoopPolicy":
#     asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

app = FastAPI()

# Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:8080", "https://gpt-api-production-8b3d.up.railway.app"],  # Разрешить все источники
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],  # Добавьте POST, если нужно
    allow_headers=["*"],
    
)

@app.get("/DeepSeek/{prompt}", tags=['Запрос чату гпт_DeepSeek'], summary='DeepSeek')
def DeepSeek_generate_answer_gpt(prompt: str):
    client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=token,
    )
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