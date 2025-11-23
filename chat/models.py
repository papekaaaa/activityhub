from django.db import models
from django.conf import settings
from post.models import Post

class ChatRoom(models.Model):
    ROOM_TYPE_CHOICES = [
        ('GROUP', 'Group Activity'),
        ('DM', 'Direct Message'),
    ]

    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES)
    name = models.CharField(max_length=255)
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True, blank=True,
        related_name='chat_room'
    )  # ใช้กับ GROUP (ห้องของกิจกรรม)

    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='created_chat_rooms'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    members = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        through='ChatMembership',
        related_name='chat_rooms'
    )

    def __str__(self):
        return f"{self.get_room_type_display()} - {self.name}"


class ChatMembership(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    is_admin = models.BooleanField(default=False)
    joined_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('room', 'user')

    def __str__(self):
        return f"{self.user} in {self.room}"


class ChatMessage(models.Model):
    room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE, related_name='messages')
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # option เผื่อทำ unread badge
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.sender} @ {self.room}: {self.content[:30]}"
