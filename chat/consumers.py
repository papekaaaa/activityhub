import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from .models import ChatRoom, ChatMessage, ChatMembership

User = get_user_model()

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close()
            return

        # เช็คว่าเป็นสมาชิกห้องนี้ไหม
        is_member = await self._is_member(user.id, self.room_id)
        if not is_member:
            await self.close()
            return

        # join group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data=None, bytes_data=None):
        data = json.loads(text_data)
        message = data.get('message', '').strip()
        user = self.scope["user"]

        if not message:
            return

        # save message DB
        msg_obj = await self._create_message(user.id, self.room_id, message)

        # broadcast
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': msg_obj.content,
                'sender_id': user.id,
                'sender_name': user.get_full_name() or user.username,
                'created_at': msg_obj.created_at.strftime('%d/%m/%Y %H:%M'),
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event['message'],
            'sender_id': event['sender_id'],
            'sender_name': event['sender_name'],
            'created_at': event['created_at'],
        }))

    # ---------- DB helpers ----------

    @database_sync_to_async
    def _is_member(self, user_id, room_id):
        return ChatMembership.objects.filter(
            room_id=room_id,
            user_id=user_id
        ).exists()

    @database_sync_to_async
    def _create_message(self, user_id, room_id, content):
        user = User.objects.get(id=user_id)
        room = ChatRoom.objects.get(id=room_id)
        return ChatMessage.objects.create(
            room=room,
            sender=user,
            content=content,
        )
