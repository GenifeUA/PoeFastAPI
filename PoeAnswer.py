import json

import poe
from starlette.responses import StreamingResponse


class POEAnswer:
    def __init__(self, poe_model: str, token: str, messages: list, stream: bool):
        self.poe_model = poe_model
        self.token = token
        self.messages = messages
        self.stream = stream

        self.prompt_tokens = 0

    def get_poe_answer(self):
        # В зависимости от типа запроса отдаём разные типы ответов - цельный и по частям.
        if self.stream:
            return StreamingResponse(self.stream_answer(), media_type="text/event-stream")
        else:
            return self.normal_answer()

    def normal_answer(self):
        client = poe.Client(self.token)

        reply = ""
        for chunk in client.send_message(self.poe_model, self.messages, with_chat_break=True):
            # Записываем ответ по кусочкам в одну переменную
            reply += chunk["text_new"]

        client.disconnect_ws()
        return {
            "text": reply
        }

    def stream_answer(self):
        client = poe.Client(self.token)

        for chunk in client.send_message(self.poe_model, self.messages, with_chat_break=True):
            for i in chunk["text_new"]:
                # Отдаём по кусочкам
                data = {
                    "text": i
                }
                yield json.dumps(data) + "\n"
        client.disconnect_ws()
