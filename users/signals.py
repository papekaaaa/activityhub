from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import User, Profile

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal นี้จะทำงานทุกครั้งที่ User object ถูก save
    """
    if created:
        # ถ้าเป็น "การสร้าง" User ใหม่ (created=True)
        # ให้สร้าง Profile ที่เชื่อมกับ User คนนั้นทันที
        Profile.objects.create(user=instance)