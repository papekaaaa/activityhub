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
        # ไม่จำกัดจำนวน => ไม่ต้องมี "เต็มแล้ว"
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
    """
    เก็บ instance._old สำหรับเทียบความเปลี่ยนแปลงหลัง save
    """
    if not instance.pk:
        instance._old = None
        return
    try:
        instance._old = Post.objects.get(pk=instance.pk)
    except Post.DoesNotExist:
        instance._old = None


@receiver(post_save, sender=Post)
def notify_users_when_post_updated(sender, instance: Post, created, **kwargs):
    if created:
        return

    old = getattr(instance, "_old", None)
    if old is None:
        return

    # ฟิลด์ที่ถือว่าสำคัญต่อความเข้าใจร่วมกัน
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
        # ระบุ old -> new แบบชัดๆ
        old_dt = old.event_date.strftime("%d/%m/%Y %H:%M") if old.event_date else "-"
        new_dt = instance.event_date.strftime("%d/%m/%Y %H:%M") if instance.event_date else "-"
        changed.append(f"วันเวลา (เดิม {old_dt} → ใหม่ {new_dt})")

    if not changed:
        return

    today = timezone.localdate()
    change_text = ", ".join(changed)

    # ผู้สมัคร
    reg_user_ids = (
        ActivityRegistration.objects.filter(post=instance, user__isnull=False)
        .values_list("user_id", flat=True)
        .distinct()
    )

    # ผู้จัดเก็บ (M2M)
    saved_user_ids = instance.saves.values_list("id", flat=True)

    # รวม + กันซ้ำ + ไม่ส่งให้เจ้าของซ้ำ (จะให้เจ้าของรู้ก็ได้ แต่โจทย์เน้นผู้สมัคร+ผู้จัดเก็บ)
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
