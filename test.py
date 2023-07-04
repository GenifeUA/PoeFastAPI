import requests

messages = [{'role': 'user', 'content': "Hi!"}]

data = {"poe_model": "beaver", "token": "", "proxy": "",
        "messages": messages, "stream": False}

response = requests.post("http://127.0.0.1:11000/poe/generation", json=data)

print(response.text)
