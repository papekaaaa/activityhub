from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from django.utils import timezone

from post.models import Post
from activity_register.models import ActivityRegistration
from .models import Notification


def _capacity_status_text(post: Post, reg_count: int) -> str:
    cap = getattr(post, "slots_available", None)
    if cap is None or cap <= 0:
        return "กิจกรรมนี้ไม่จำกัดจำนวน"

    remaining = cap - reg_count
    if remaining <= 0:
        return f"ตอนนี้กิจกรรมเต็มแล้ว (สมัคร {reg_count}/{cap})"
    return f"ตอนนี้สมัครแล้ว {reg_count}/{cap} เหลือ {remaining} ที่"


# -------------------------
# (2) แจ้งผู้สร้างทันทีเมื่อกิจกรรมเต็ม
# -------------------------
@receiver(post_save, sender=ActivityRegistration)
def notify_owner_when_full(sender, instance: ActivityRegistration, created, **kwargs):
    if not created:
        return

    post = instance.post
    if not post or post.is_deleted or post.is_hidden or post.status != "APPROVED":
        return

    cap = getattr(post, "slots_available", None)
    if cap is None or cap <= 0:
        return

    reg_count = ActivityRegistration.objects.filter(post=post).count()
    if reg_count < cap:
        return

    today = timezone.localdate()
    status_text = _capacity_status_text(post, reg_count)

    Notification.objects.get_or_create(
        user=post.organizer,
        post=post,
        kind=Notification.Kind.OWNER_FULL,
        trigger_date=today,
        defaults={
            "title": post.title,
            "message": f"กิจกรรมของคุณเต็มแล้ว\n{status_text}",
            "link_url": f"/post/{post.id}/",
        },
    )


# -------------------------
# (4) แจ้งผู้สมัคร + ผู้จัดเก็บ เมื่อเจ้าของแก้โพสต์/เปลี่ยนวันที่
# -------------------------
@receiver(pre_save, sender=Post)
def snapshot_old_post(sender, instance: Post, **kwargs):
    if not instance.pk:
        instance._old = None
        return
    try:
        instance._old = Post.objects.get(pk=instance.pk)
    except Post.DoesNotExist:
        instance._old = None


@receiver(post_save, sender=Post)
def notify_users_when_post_updated(sender, instance: Post, created, **kwargs):
    """
    แจ้งเตือนเมื่อโพสต์มีการเปลี่ยนแปลง:
    - แก้ไข → แจ้งผู้สมัคร + ผู้จัดเก็บ
    - ซ่อน/ลบ (โดยแอดมิน) → แจ้งผู้สมัคร + เจ้าของโพสต์ด้วย
    """
    if created:
        # ✅ แจ้งเตือนผู้ติดตามเมื่อมีโพสต์ใหม่
        _notify_followers_new_post(instance)
        return

    old = getattr(instance, "_old", None)
    if old is None:
        return

    today = timezone.localdate()

    # ✅ ตรวจสอบว่าถูกลบ/ซ่อนหรือไม่ (admin action)
    was_deleted = not old.is_deleted and instance.is_deleted
    was_hidden = not old.is_hidden and instance.is_hidden

    if was_deleted or was_hidden:
        action_text = "ถูกลบ" if was_deleted else "ถูกซ่อน"
        kind = Notification.Kind.POST_DELETED if was_deleted else Notification.Kind.POST_HIDDEN

        # แจ้งผู้สมัคร
        reg_user_ids = (
            ActivityRegistration.objects.filter(post=instance, user__isnull=False)
            .values_list("user_id", flat=True)
            .distinct()
        )
        # แจ้งเจ้าของโพสต์ด้วย (กรณีแอดมินลบ)
        target_ids = set(reg_user_ids)
        if instance.organizer_id:
            target_ids.add(instance.organizer_id)

        for uid in target_ids:
            Notification.objects.get_or_create(
                user_id=uid,
                post=instance,
                kind=kind,
                trigger_date=today,
                defaults={
                    "title": instance.title,
                    "message": f"กิจกรรม \"{instance.title}\" {action_text}โดยผู้ดูแลระบบ",
                    "link_url": f"/post/{instance.id}/",
                },
            )
        return

    # ✅ ตรวจสอบการแก้ไขฟิลด์
    changed = []

    if old.title != instance.title:
        changed.append("ชื่อกิจกรรม")
    if old.location != instance.location:
        changed.append("สถานที่")
    if old.description != instance.description:
        changed.append("รายละเอียด")
    if old.category != instance.category:
        changed.append("ประเภทกิจกรรม")
    if old.slots_available != instance.slots_available:
        changed.append("จำนวนที่รับสมัคร")
    if old.fee != instance.fee:
        changed.append("ค่าใช้จ่าย")
    if old.allow_register != instance.allow_register:
        changed.append("สถานะการเปิดรับสมัคร")
    if old.event_date != instance.event_date:
        old_dt = old.event_date.strftime("%d/%m/%Y %H:%M") if old.event_date else "-"
        new_dt = instance.event_date.strftime("%d/%m/%Y %H:%M") if instance.event_date else "-"
        changed.append(f"วันเวลา (เดิม {old_dt} → ใหม่ {new_dt})")

    if not changed:
        return

    change_text = ", ".join(changed)

    # ผู้สมัคร
    reg_user_ids = (
        ActivityRegistration.objects.filter(post=instance, user__isnull=False)
        .values_list("user_id", flat=True)
        .distinct()
    )

    # ผู้จัดเก็บ (M2M)
    saved_user_ids = instance.saves.values_list("pk", flat=True)

    target_ids = set(reg_user_ids) | set(saved_user_ids)
    if instance.organizer_id in target_ids:
        target_ids.remove(instance.organizer_id)

    for uid in target_ids:
        Notification.objects.get_or_create(
            user_id=uid,
            post=instance,
            kind=Notification.Kind.POST_UPDATED,
            trigger_date=today,
            defaults={
                "title": instance.title,
                "message": f"เจ้าของกิจกรรมได้แก้ไขโพสต์: {change_text}\nกรุณาตรวจสอบรายละเอียดอีกครั้ง",
                "link_url": f"/post/{instance.id}/",
            },
        )


# -------------------------
# (5) แจ้งผู้ติดตามเมื่อมีโพสต์ใหม่
# -------------------------
def _notify_followers_new_post(post: Post):
    """เมื่อผู้ใช้สร้างโพสต์ใหม่ แจ้งเตือนผู้ที่ติดตามอยู่"""
    try:
        from users.models import Profile
        organizer_profile = Profile.objects.get(user=post.organizer)
        # followers ของ organizer คือ Profile ที่อยู่ใน followers M2M
        follower_profiles = organizer_profile.followers.all()

        today = timezone.localdate()

        for fp in follower_profiles:
            Notification.objects.get_or_create(
                user=fp.user,
                post=post,
                kind=Notification.Kind.FOLLOWER_NEW_POST,
                trigger_date=today,
                defaults={
                    "title": post.title,
                    "message": f"{post.organizer.get_full_name() or post.organizer.email} ได้โพสต์กิจกรรมใหม่: \"{post.title}\"",
                    "link_url": f"/post/{post.id}/",
                },
            )
    except Exception:
        pass


# -------------------------
# (6) แจ้งเตือนข้อความแชทใหม่
# -------------------------
def notify_chat_message(sender_user, room, message_preview=""):
    """เรียกใช้จาก chat consumer/view เมื่อมีข้อความใหม่"""
    from chat.models import ChatMembership
    today = timezone.localdate()

    members = ChatMembership.objects.filter(room=room).exclude(user=sender_user)
    room_name = room.name or "ห้องแชท"

    for m in members:
        # ไม่ใช้ get_or_create กับ trigger_date เพื่อให้แจ้งทุกครั้ง
        Notification.objects.create(
            user=m.user,
            kind=Notification.Kind.CHAT_MESSAGE,
            title=f"ข้อความใหม่จาก {sender_user.get_full_name() or sender_user.email}",
            message=message_preview[:100] if message_preview else "ส่งข้อความมาหาคุณ",
            link_url=f"/chat/dm/{sender_user.email}/" if room.room_type == "DM" else f"/chat/activity/{room.post_id}/" if room.post_id else "/chat/inbox/",
        )
