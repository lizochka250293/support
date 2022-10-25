import requests
from .token import api_token, channel_id
API = api_token
HOST = 'https://retail-support.rendez-vous.ru'
CHANNEL = channel_id
def send_telegram(text: str, number: str):
    """Отправка в тг"""
    url = "https://api.telegram.org/bot"
    url += API
    method = url + "/sendMessage"
    to_send = f'{text}, {HOST}/chat_room/{number}/'
    r = requests.post(method, data={
        "chat_id": CHANNEL,
        "text": to_send
    })
