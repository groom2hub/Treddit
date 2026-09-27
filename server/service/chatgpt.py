from fastapi import HTTPException
from openai import OpenAI, OpenAIError
from pydantic import BaseModel

from config import settings


class Conversation(BaseModel):
    history: list


def get_answer(data: Conversation):
    if not settings.openai_key:
        raise HTTPException(status_code=503, detail="OpenAI API 키가 설정되지 않았습니다.")

    client = OpenAI(api_key=settings.openai_key)
    try:
        response = client.chat.completions.create(model=settings.openai_model, messages=data.history)
    except OpenAIError:
        raise HTTPException(status_code=502, detail="OpenAI API 호출에 실패했습니다.")

    return {"answer": response.choices[0].message.content}
