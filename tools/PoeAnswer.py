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
        logger.info(f"response for {self.poe_model} using {self.token} token with {self.proxy} proxy!")

        if self.stream:
            return StreamingResponse(self.stream_answer(), media_type="text/event-stream")
        else:
            return self.normal_answer()

    def normal_answer(self):
        client = poe.Client(self.token, proxy=self.proxy)
        try:
            response = ""
            for chunk in client.send_message(self.poe_model, self.messages):
                # Записываем ответ по кусочкам в одну переменную
                response += chunk["text_new"]

            return Response(content=response, media_type="text/plain")
        finally:
            Thread(target=finish_response, args=(client, self.poe_model)).start()

    def stream_answer(self):
        client = poe.Client(self.token, proxy=self.proxy)
        try:
            for chunk in client.send_message(self.poe_model, self.messages):
                for i in chunk["text_new"]:
                    # Отдаём по кусочкам
                    yield i
        finally:
            Thread(target=finish_response, args=(client, self.poe_model)).start()
