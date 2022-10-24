import requests


def send_telegram(text: str, number: str):
    """Отправка в тг"""
    host = ''
    api_token = "5440252830:AAG15UZiZ1v_EaclQ85YXRKBc86DNN40UCo"
    url = "https://api.telegram.org/bot"
    channel_id = -1001658312828
    url += api_token
    method = url + "/sendMessage"
    to_send = f'{text}, http://{host}/chat_room/{number}/'
    r = requests.post(method, data={
        "chat_id": channel_id,
        "text": to_send
    })
