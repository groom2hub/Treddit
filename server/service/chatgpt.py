import openai
from pydantic import BaseModel
from config import settings

class Conversation(BaseModel):
    history: list

openai.api_key = settings.openai_key

def get_answer(data: Conversation):
    response = openai.ChatCompletion.create(
         model="gpt-3.5-turbo",
         messages=data.history
    )
    answer = response['choices'][0]['message']['content']
    return {"answer": answer}