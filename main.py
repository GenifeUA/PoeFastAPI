from typing import Optional

from fastapi import FastAPI
from pydantic import BaseModel

from tools.PoeAnswer import POEAnswer

app = FastAPI()


class ChatCompletionData(BaseModel):
    poe_model: str
    token: str
    proxy: Optional[str] = None
    messages: str
    stream: Optional[bool] = False


@app.post('/poe/generation')
def completion(data: ChatCompletionData):
    return POEAnswer(data.poe_model, data.token, data.proxy, data.messages, data.stream).get_response()
