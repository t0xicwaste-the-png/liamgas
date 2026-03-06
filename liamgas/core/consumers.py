import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth.models import User
from .models import ChatRoom, Message

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        print(f"WebSocket connect attempt for room {self.scope['url_route']['kwargs']['room_id']}")
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.accept()
        print(f"WebSocket connected for room {self.room_id}")

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        user = self.scope['user']

        if user.is_authenticated:
            # Save message to database
            saved_message = await self.save_message(user, message)

            # Send message to room group
            await self.channel_layer.group_send(
                self.room_group_name,
                {
                    'type': 'chat_message',
                    'message': message,
                    'user': user.username,
                    'timestamp': saved_message.timestamp.isoformat()
                }
            )
        else:
            # Send error message back to WebSocket
            await self.send(text_data=json.dumps({
                'error': 'User not authenticated'
            }))

    # Receive message from room group
    async def chat_message(self, event):
        message = event['message']
        user = event['user']
        timestamp = event['timestamp']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'user': user,
            'timestamp': timestamp
        }))

    @database_sync_to_async
    def save_message(self, user, message):
        room = ChatRoom.objects.get(id=self.room_id)
        return Message.objects.create(
            room=room,
            user=user,
            content=message
        )