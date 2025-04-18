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
import logging

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

DEBUG = True
valueDebug = os.getenv("debug")
if valueDebug == 1:
    DEBUG = True
elif valueDebug == 0:
    DEBUG = False  


print(valueDebug)
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
        if DEBUG == True:
            if completion:
                logger.debug(f"completion: {completion}")
                if completion.choices:
                    logger.debug(f"completion.choices: {completion.choices}")
                    if len(completion.choices) > 0:
                        logger.debug(f"completion.choices[0]: {completion.choices[0]}")
                        if completion.choices[0].message:
                            logger.debug(f"completion.choices[0].message: {completion.choices[0].message}")
                            if completion.choices[0].message.content:
                                example = completion.choices[0].message.content
                                answer = GetExample(example)
                                return JSONResponse(content={"example": example, "answer": answer})
                            else:
                                logger.warning("completion.choices[0].message.content is None")
                        else:
                            logger.warning("completion.choices[0].message is None")
                    else:
                        logger.warning("len(completion.choices) is 0")
                else:
                    logger.warning("completion.choices is None")
            else:
                logger.warning("completion is None")
        else:
             if completion.choices[0].message.content:
                                example = completion.choices[0].message.content
                                answer = GetExample(example)
                                return JSONResponse(content={"example": example, "answer": answer})
        #return JSONResponse(content={"error": "Модель не вернула результат"}, status_code=400)

    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)
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


# if __name__ == '__main__':
   #  app.run(debug=True, port=os.getenv("PORT", default=5000))  FOR SERVICE
#    app.run(debug=True)  # FOR LOCALHOST



