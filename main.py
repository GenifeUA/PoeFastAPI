from typing import Optional

import uvicorn as uvicorn
from fastapi import FastAPI
from pydantic import conlist, BaseModel

from PoeAnswer import POEAnswer

app = FastAPI()


class ChatCompletionData(BaseModel):
    poe_model: str
    token: str
    messages: conlist(dict, min_items=1)
    stream: Optional[bool] = False


@app.post('/poe/generation')
def completion(data: ChatCompletionData):
    # Получаем нейросеть для запроса
    poe_model = data.poe_model

    answer = POEAnswer(poe_model, data.token, data.messages, data.stream)
    return answer.get_poe_answer()


uvicorn.run(app)
