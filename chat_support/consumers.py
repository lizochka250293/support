from channels.db import database_sync_to_async
from channels.generic.websocket import AsyncWebsocketConsumer
import json
from channels.generic.http import AsyncHttpConsumer
from channels.generic.websocket import AsyncWebsocketConsumer
from django.contrib.auth import get_user_model

from chat_support.models import ChatMessage, ChatDialog, User

user = get_user_model()


class ChatConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = 'chat_%s' % self.room_name
        self.sen = self.scope["session"]
        print(self.sen.session_key)
        # self.user = self.scope["user"]
        # Join room group

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)

        if text_data_json.get('action') == 'close':
            await self.chat_close(text_data_json.get('chat'))
            return

        message = text_data_json['message']
        # username = text_data_json['user']
        username = self.scope["user"]
        print(username, type(username))
        print('name', username)

        # send_telegram(message)
        await self.write_message(message, username)

        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': message,
                'username': await self.get_username(username)
            }
        )

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'username': event['username']
        }))


    @database_sync_to_async
    def get_username(self, username):
        user = User.objects.get(username=username).username
        print(user)
        return user

    @database_sync_to_async
    def write_message(self, message, username):
        ChatMessage.objects.create(dialog_id=self.room_name, body=message, author=user.objects.get(username=username))

    @database_sync_to_async
    def chat_close(self, dialog):
        dialog_close = ChatDialog.objects.get(id=dialog)
        dialog_close.is_active = False
        dialog_close.save()


class LongPollConsumer(AsyncHttpConsumer):
    async def handle(self, body):
        await self.send_headers(headers=[
            (b"Content-Type", b"application/json"),
        ])
        # Headers are only sent after the first body event.
        # Set "more_body" to tell the interface server to not
        # finish the response yet:
        await self.send_body(b"", more_body=True)

    async def chat_message(self, event):
        # Send JSON and finish the response:
        await self.send_body(json.dumps(event).encode("utf-8"))
