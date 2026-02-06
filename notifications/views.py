from datetime import timedelta
from django.apps import apps
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden
from django.utils import timezone
from django.views.decorators.http import require_GET, require_POST

from .models import Notification


def _get_registration_model():
    candidates = [
        ("activity_register", "ActivityRegistration"),
        ("activity_register", "Registration"),
        ("activity_register", "ActivityRegister"),
    ]
    for app_label, model_name in candidates:
        try:
            model = apps.get_model(app_label, model_name)
            if model:
                return model
        except LookupError:
            continue
    return None


def _capacity_status_text(post, reg_count: int | None = None) -> str:
    """
    คืนข้อความสถานะความจุ:
    - ไม่จำกัด (กรณี slots_available <= 0 หรือ None)
    - เต็มแล้ว / เหลือที่ว่าง
    """
    cap = getattr(post, "slots_available", None)
    if cap is None or cap <= 0:
        return "กิจกรรมนี้ไม่จำกัดจำนวน"

    if reg_count is None:
        # ใช้ related_name='registrations' ที่คุณมีอยู่แล้ว
        try:
            reg_count = post.registrations.count()
        except Exception:
            reg_count = 0

    remaining = cap - reg_count
    if remaining <= 0:
        return f"ตอนนี้กิจกรรมเต็มแล้ว (สมัคร {reg_count}/{cap})"
    return f"ตอนนี้สมัครแล้ว {reg_count}/{cap} เหลือ {remaining} ที่"


def _ensure_activity_notifications(user):
    """
    สร้างแจ้งเตือนตามกติกา (lazy: สร้างตอนเปิดกระดิ่ง):
    1) ผู้บันทึก: เตือนก่อน 3 วัน และ 1 วัน + แนบสถานะที่นั่ง
    2) ผู้สมัคร: เตือนก่อน 1 วัน
    3) ผู้สร้างกิจกรรม: เตือนก่อน 2 วัน + แนบสถานะผู้สมัคร/ความจุ
    """
    today = timezone.localdate()
    d1 = today + timedelta(days=1)
    d2 = today + timedelta(days=2)
    d3 = today + timedelta(days=3)

    Post = apps.get_model("post", "Post")

    base_post_filter = dict(
        is_deleted=False,
        is_hidden=False,
        status="APPROVED",
    )

    # -------------------------
    # (1) Saved reminders: 3 วันก่อน + 1 วันก่อน
    # -------------------------
    saved_posts_3 = user.saved_posts.filter(
        event_date__date=d3,
        **base_post_filter,
    )
    for p in saved_posts_3:
        status_text = _capacity_status_text(p)
        Notification.objects.get_or_create(
            user=user,
            post=p,
            kind=Notification.Kind.SAVED_REMINDER,
            trigger_date=d3,
            defaults={
                "title": p.title,
                "message": f"กิจกรรมที่คุณจัดเก็บ จะเริ่มในอีก 3 วัน\n{status_text}",
                "link_url": f"/post/{p.id}/",
            },
        )

    saved_posts_1 = user.saved_posts.filter(
        event_date__date=d1,
        **base_post_filter,
    )
    for p in saved_posts_1:
        status_text = _capacity_status_text(p)
        Notification.objects.get_or_create(
            user=user,
            post=p,
            kind=Notification.Kind.SAVED_REMINDER,
            trigger_date=d1,
            defaults={
                "title": p.title,
                "message": f"กิจกรรมที่คุณจัดเก็บ จะเริ่มในอีก 1 วัน\n{status_text}",
                "link_url": f"/post/{p.id}/",
            },
        )

    # -------------------------
    # (2) Register reminder: 1 วันก่อน (ผู้สมัคร)
    # -------------------------
    RegModel = _get_registration_model()
    if RegModel:
        reg_qs = RegModel.objects.filter(user=user).select_related("post")
        for reg in reg_qs:
            p = getattr(reg, "post", None)
            if not p or not getattr(p, "event_date", None):
                continue

            if timezone.localdate(p.event_date) == d1 and (not p.is_deleted) and (not p.is_hidden) and (p.status == "APPROVED"):
                status_text = _capacity_status_text(p)
                Notification.objects.get_or_create(
                    user=user,
                    post=p,
                    kind=Notification.Kind.REGISTER_REMINDER,
                    trigger_date=d1,
                    defaults={
                        "title": p.title,
                        "message": f"กิจกรรมที่คุณสมัคร จะเริ่มในอีก 1 วัน\n{status_text}",
                        "link_url": f"/post/{p.id}/",
                    },
                )

    # -------------------------
    # (3) Owner status reminder: 2 วันก่อน (ผู้สร้างกิจกรรม)
    # -------------------------
    owner_posts = Post.objects.filter(
        organizer=user,
        event_date__date=d2,
        **base_post_filter,
    )
    for p in owner_posts:
        # จำนวนผู้สมัคร
        try:
            reg_count = p.registrations.count()
        except Exception:
            reg_count = 0

        status_text = _capacity_status_text(p, reg_count=reg_count)
        Notification.objects.get_or_create(
            user=user,
            post=p,
            kind=Notification.Kind.OWNER_STATUS_REMINDER,
            trigger_date=d2,
            defaults={
                "title": p.title,
                "message": f"อีก 2 วันกิจกรรมจะเริ่ม\nสถานะตอนนี้: {status_text}",
                "link_url": f"/post/{p.id}/",
            },
        )


@login_required
@require_GET
def api_list_notifications(request):
    _ensure_activity_notifications(request.user)

    qs = Notification.objects.filter(user=request.user).order_by("-created_at")[:30]
    data = []
    for n in qs:
        data.append(
            {
                "id": n.id,
                "kind": n.kind,
                "title": n.title,
                "message": n.message,
                "link_url": n.link_url,
                "is_read": n.is_read,
                "created_at": n.created_at.isoformat(),
            }
        )

    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({"unread": unread_count, "items": data})


@login_required
@require_POST
def api_mark_read(request, notif_id):
    try:
        n = Notification.objects.get(id=notif_id)
    except Notification.DoesNotExist:
        return JsonResponse({"ok": False}, status=404)

    if n.user_id != request.user.id:
        return HttpResponseForbidden("forbidden")

    n.is_read = True
    n.save(update_fields=["is_read"])
    unread_count = Notification.objects.filter(user=request.user, is_read=False).count()
    return JsonResponse({"ok": True, "unread": unread_count})
