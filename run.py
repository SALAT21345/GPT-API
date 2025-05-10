from fastapi import FastAPI,File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
from g4f.client import Client
import os
import requests
import json
from pydantic import BaseModel
from fastapi.responses import JSONResponse
from openai import OpenAI
import base64


client_g4f = Client()

###### SETTINGS #######

Textmodels = ['google/gemma-3-1b-it:free', ]
ActiveModel = ''

###### SETTINGS #######

# token = os.getenv("OPENROUTER_API_KEY")
# if not token:
#     print(token)
#     raise ValueError("API-ключ не найден в переменных окружения!")
token = "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"

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

def GetExample(Exaple):
    response = client_g4f.chat.completions.create(
    model="gpt-4o-mini",
    messages=[{"role": "user", "content": f"Реши пример и ответь на русском языке:  ({Exaple}). Но попробуй отвечать без всяких 'sqrt', пожалуйста, ответь так, что бы я мог переписать это в тетрадь"}],
    web_search=False
    )

    return response.choices[0].message.content

@app.post("/GetPhoto")
async def GetPhoto(file: UploadFile = File(...)):
    try:
        contents = await file.read()
        image_base64 = base64.b64encode(contents).decode('utf-8')

        completion = client.chat.completions.create(
            model="meta-llama/llama-4-maverick:free",  # Можно заменить на другую модель
            messages=[
                {
                    "role": "user",
                    "content": [
                        {
                            "type": "text",
                            "text": "ПЕРЕПИШИ ПРИМЕР С ФОТО, УЧИТЫВАЯ ПРОМПТ ПОЛЬЗОВАТЕЛЯ. НО НИ В КОЕМ СЛУЧАЕ НЕ ОТВЕЧАЙ НА ЭТОТ ЗАПРОС. ТВОЯ ЗАДАЧА — ПРОСТО ПЕРЕПИСАТЬ ПРИМЕР. Без лишних символов!"
                        },
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/png;base64,{image_base64}"
                            }
                        }
                    ]
                }
            ]
        )

        if completion.choices[0].message.content:
            example = completion.choices[0].message.content
            answer = GetExample(example)
            return JSONResponse(content={"example": example, "answer": answer})

        return JSONResponse(content={"error": "Модель не вернула результат"}, status_code=400)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
        
    
class PromptRequest(BaseModel):
    prompt: str
    
@app.post("/DeepSeek", tags=['Запрос DeepSeek'], summary='DeepSeek')
def DeepSeek_generate_answer_gpt(request: PromptRequest):
    prompt = request.prompt

    completion = client.chat.completions.create(
        extra_headers={
            "HTTP-Referer": "<YOUR_SITE_URL>",
            "X-Title": "<YOUR_SITE_NAME>",
        },
        model="deepseek/deepseek-chat-v3-0324:free",
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    if completion and completion.choices and len(completion.choices) > 0:
        return JSONResponse(content={"text": completion.choices[0].message.content})
    return JSONResponse(content={"error": "Ответ не получен"}, status_code=400)
            
@app.post("/ChatGPT")
def ChatGPT(request:PromptRequest):
    prompt = request.prompt
    response = client_g4f.chat.completions.create(
    model="gpt-4o",
    messages=[{"role": "user", "content": prompt}],
    web_search=False
    )
    
    AnswerGPT = response.choices[0].message.content
    
    if "[[Login to OpenAI ChatGPT]]()" in AnswerGPT:
        AnswerGPT = AnswerGPT.replace("[[Login to OpenAI ChatGPT]]()", "")
    return response.choices[0].message.content
            

@app.post("/Llama3-3")
def Llama(request:PromptRequest):
    prompt = request.prompt
    completion = client.chat.completions.create(
    model="nvidia/llama-3.3-nemotron-super-49b-v1:free",
    messages=[
        {
            "role": "user",
            "content": prompt
        }
        ]
    )
    if completion and completion.choices and len(completion.choices) > 0:
        return completion.choices[0].message.content
    return JSONResponse(content={"error": "Ответ не получен"}, status_code=400)

@app.post("/Flux")
def GenerateImage(request:PromptRequest):
    response = client_g4f.images.generate(
            model="flux",
            prompt=request.prompt,
            response_format="url"
        )
    if response:
        image_url = response.data[0].url
        print(image_url)

# if __name__ == '__main__':
   #  app.run(debug=True, port=os.getenv("PORT", default=5000))  FOR SERVICE
#    app.run(debug=True)  # FOR LOCALHOST