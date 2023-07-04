from threading import Thread
from time import sleep

import poe
from starlette.responses import StreamingResponse, Response

from tools.Logger import logger


def finish_response(client: poe.Client, model):
    sleep(5)
    try:
        client.send_chat_break(model)
    except RuntimeError as e:
        logger.error(f"Error on final chat break: {e}")
    try:
        client.ws_error = False
        client.disconnect_ws()
    except RuntimeError as e:
        logger.error(f"Error on disconnect_ws: {e}")


class POEAnswer:
    def __init__(self, poe_model: str, token: str, proxy: str, messages: str, stream: bool):
        self.poe_model = poe_model
        self.token = token
        self.proxy = proxy
        self.messages = messages
        self.stream = stream

    def get_poe_answer(self):
        # В зависимости от типа запроса отдаём разные типы ответов - цельный и по частям.
        logger.info(f"response for {self.poe_model} using {self.token} token with {self.proxy} proxy!")
        
        if self.stream:
            return StreamingResponse(self.stream_answer(), media_type="text/event-stream")
        else:
            return self.normal_answer()

    def normal_answer(self):
        client = None
        try:
            client = poe.Client(self.token, proxy=self.proxy)

            reply = ""
            for chunk in client.send_message(self.poe_model, self.messages):
                # Записываем ответ по кусочкам в одну переменную
                reply += chunk["text_new"]

            return Response(content=reply, media_type="text/plain")
        finally:
            if client:
                Thread(target=finish_response, args=(client, self.poe_model)).start()

    def stream_answer(self):
        client = None
        try:
            client = poe.Client(self.token, proxy=self.proxy)

            for chunk in client.send_message(self.poe_model, self.messages):
                for i in chunk["text_new"]:
                    # Отдаём по кусочкам
                    yield i
        finally:
            if client:
                Thread(target=finish_response, args=(client, self.poe_model)).start()
