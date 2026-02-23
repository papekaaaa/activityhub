import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.contrib.auth import get_user_model
from django.utils.timezone import localtime
from zoneinfo import ZoneInfo

from .models import ChatRoom, ChatMessage, ChatMembership

User = get_user_model()
BKK_TZ = ZoneInfo("Asia/Bangkok")


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['room_id']
        self.room_group_name = f'chat_{self.room_id}'

        user = self.scope["user"]
        if not user.is_authenticated:
            await self.close()
            return

        is_member = await self._is_member(user.pk, self.room_id)
        if not is_member:
            await self.close()
            return

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
        message = (data.get('message') or '').strip()
        user = self.scope["user"]

        if not message:
            return

        msg_obj = await self._create_message(user.pk, self.room_id, message)

        # ✅ บังคับเป็นเวลาไทย
        dt_local = localtime(msg_obj.created_at, timezone=BKK_TZ)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'message': msg_obj.content,
                'sender_id': str(user.pk),
                'sender_name': user.get_full_name() or str(user.pk),
                'created_at': dt_local.strftime('%d/%m/%Y %H:%M'),
                'created_at_iso': dt_local.isoformat(),
                'file_url': '',
                'file_name': '',
                'is_image': False,
            }
        )

        # ✅ แจ้งเตือนข้อความแชทใหม่
        await self._notify_chat(user.pk, self.room_id, message)

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            'message': event.get('message', ''),
            'sender_id': event.get('sender_id'),
            'sender_name': event.get('sender_name'),
            'created_at': event.get('created_at', ''),
            'created_at_iso': event.get('created_at_iso', ''),
            'file_url': event.get('file_url', ''),
            'file_name': event.get('file_name', ''),
            'is_image': event.get('is_image', False),
        }))

    # ---------- DB helpers ----------

    @database_sync_to_async
    def _is_member(self, user_id, room_id):
        return ChatMembership.objects.filter(
            room_id=room_id,
            user_id=user_id
        ).exists()

    @database_sync_to_async
    def _create_message(self, user_pk, room_id, content):
        user = User.objects.get(pk=user_pk)
        room = ChatRoom.objects.get(id=room_id)
        return ChatMessage.objects.create(
            room=room,
            sender=user,
            content=content,
        )

    @database_sync_to_async
    def _notify_chat(self, user_pk, room_id, message):
        try:
            from notifications.signals import notify_chat_message
            user = User.objects.get(pk=user_pk)
            room = ChatRoom.objects.get(id=room_id)
            notify_chat_message(user, room, message)
        except Exception:
            pass
