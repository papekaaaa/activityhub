from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Avg
from .models import Post
from .forms import PostForm
from activity_register.models import ActivityReview, ActivityRegistration
from chat.models import ChatRoom, ChatMembership
import json


# ------------------------------
# ฟังก์ชัน: สร้างกิจกรรมใหม่
# ------------------------------
@login_required
def create_post(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.organizer = request.user
            post.map_lat = request.POST.get('map_lat') or None
            post.map_lng = request.POST.get('map_lng') or None
            post.save()

            if post.create_group:
                room = ChatRoom.objects.create(
                    room_type='GROUP',
                    name=post.title,
                    post=post,
                    created_by=request.user,
                )
                ChatMembership.objects.create(
                    room=room,
                    user=request.user,
                    is_admin=True,
                )

            messages.success(request, 'สร้างกิจกรรมสำเร็จ! รอการอนุมัติจากผู้ดูแลระบบ')
            return redirect('home:home')
    else:
        form = PostForm()

    profile_pic_url = None
    user = request.user

    if hasattr(user, "profile") and getattr(user.profile, "profile_picture", None):
        if user.profile.profile_picture:
            profile_pic_url = user.profile.profile_picture.url
    elif hasattr(user, "profile_picture") and user.profile_picture:
        profile_pic_url = user.profile_picture.url

    context = {
        "form": form,
        "profile_pic_url": profile_pic_url,
    }
    return render(request, 'post/create_post.html', context)


# ------------------------------
# ✅ ปิดรับสมัคร (กดจากหน้าแก้ไขโพสต์)
# ------------------------------
@login_required
@require_POST
def close_registration(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.organizer != request.user:
        return HttpResponseForbidden("คุณไม่มีสิทธิ์แก้ไขกิจกรรมนี้")

    if post.allow_register:
        post.allow_register = False
        post.save(update_fields=["allow_register"])
        messages.success(request, "ปิดรับการสมัครเรียบร้อยแล้ว")

    return redirect('post:post_edit', post_id=post.id)


# ------------------------------
# ฟังก์ชัน: แก้ไขกิจกรรม
# ------------------------------
@login_required
def post_update_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.organizer != request.user:
        return HttpResponseForbidden("คุณไม่มีสิทธิ์แก้ไขกิจกรรมนี้")

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            old_create_group = post.create_group
            old_allow_register = post.allow_register

            post = form.save(commit=False)
            post.map_lat = request.POST.get('map_lat') or None
            post.map_lng = request.POST.get('map_lng') or None
            post.save()

            # ✅ ถ้าเปิด create_group ใหม่ (เดิมปิด) → สร้างห้องแชท
            if post.create_group and not old_create_group:
                existing_room = ChatRoom.objects.filter(room_type='GROUP', post=post).first()
                if not existing_room:
                    room = ChatRoom.objects.create(
                        room_type='GROUP',
                        name=post.title,
                        post=post,
                        created_by=request.user,
                    )
                    ChatMembership.objects.get_or_create(
                        room=room,
                        user=request.user,
                        defaults={'is_admin': True},
                    )

            # ✅ ถ้าปิด create_group (เดิมเปิด) → ลบห้องแชท
            if not post.create_group and old_create_group:
                ChatRoom.objects.filter(room_type='GROUP', post=post).delete()

            messages.success(request, 'กิจกรรมของคุณได้รับการอัปเดตแล้ว!')
            return redirect('post:post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)

    return render(
        request,
        'post/post_form.html',
        {
            'form': form,
            'title': 'แก้ไขกิจกรรม',
            'post': post,
            # ✅ ใช้ใน template: ถ้า allow_register=True ให้โชว์ปุ่ม "ปิดรับการสมัคร"
            'show_close_register_button': post.allow_register,
        },
    )


# ------------------------------
# ฟังก์ชัน: ลบกิจกรรม
# ------------------------------
@login_required
def post_delete_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    if post.organizer != request.user:
        return HttpResponseForbidden("คุณไม่มีสิทธิ์ลบกิจกรรมนี้")

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'กิจกรรมของคุณถูกลบเรียบร้อยแล้ว')
        return redirect('profile')

    return render(request, 'post/post_confirm_delete.html', {'post': post})


# ------------------------------
# ฟังก์ชัน: แสดงรายละเอียดกิจกรรม + รีวิว (สำหรับ route post:post_detail)
# ------------------------------
def post_detail_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # ✅ ปิดรับสมัครอัตโนมัติเมื่อเลยวันที่จัดกิจกรรม
    if post.allow_register and post.event_date:
        from django.utils import timezone
        if post.event_date < timezone.now():
            post.allow_register = False
            post.save(update_fields=['allow_register'])

    reviews = (
        post.activity_reviews
        .select_related('user')
        .order_by('-created_at')
    )

    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    avg_rating_int = int(round(avg_rating)) if avg_rating else 0
    review_count = reviews.count()

    # ✅ สถานะการสมัครของผู้ใช้ (ใช้ทำ “สมัครแล้ว/ยกเลิก/undo” ใน template)
    my_reg = None
    if request.user.is_authenticated:
        my_reg = ActivityRegistration.objects.filter(
            user=request.user,
            post=post,
        ).first()

        # finalize pending ถ้าหมดเวลา (กันคนค้าง)
        if my_reg and my_reg.status == ActivityRegistration.Status.CANCEL_PENDING:
            my_reg.finalize_cancel_if_expired()
            my_reg.refresh_from_db()

    # ✅ ตรวจสอบว่ามี chat room หรือไม่
    has_chat_room = ChatRoom.objects.filter(post=post).exists()

    # ✅ ตรวจสอบว่าผู้ใช้สมัครแล้วหรือยัง (สถานะ ACTIVE)
    user_is_registered = False
    if my_reg and my_reg.status == 'ACTIVE':
        user_is_registered = True

    context = {
        'post': post,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'avg_rating_int': avg_rating_int,
        'review_count': review_count,
        'my_reg': my_reg,
        'active_reg_count': post.active_registrations_count(),
        'is_full': post.is_full(),
        'has_chat_room': has_chat_room,
        'user_is_registered': user_is_registered,
        'cancel_undo_until_iso': my_reg.cancel_undo_until.isoformat() if my_reg and my_reg.cancel_undo_until else '',
        'cooldown_until_iso': my_reg.cooldown_until.isoformat() if my_reg and my_reg.cooldown_until and my_reg.status == 'CANCELED' else '',
    }
    return render(request, 'post/post_detail.html', context)


# ------------------------------
# ✅ Toggle ถูกใจ
# ------------------------------
@login_required
@require_POST
def toggle_like(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    if user in post.likes.all():
        post.likes.remove(user)
        liked = False
    else:
        post.likes.add(user)
        liked = True
    return JsonResponse({'liked': liked, 'likes_count': post.likes.count()})


# ------------------------------
# ✅ Toggle จัดเก็บ
# ------------------------------
@login_required
@require_POST
def toggle_save(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    user = request.user
    if user in post.saves.all():
        post.saves.remove(user)
        saved = False
    else:
        post.saves.add(user)
        saved = True
    return JsonResponse({'saved': saved, 'saves_count': post.saves.count()})


# ------------------------------
# ฟังก์ชัน: แสดงกิจกรรมที่ถูกใจ
# ------------------------------
@login_required
def liked_posts_view(request):
    liked_posts = request.user.liked_posts.filter(
        is_hidden=False,
        is_deleted=False,
    ).order_by('-created_at')
    context = {'posts': liked_posts, 'title': 'กิจกรรมที่กดถูกใจ '}
    return render(request, 'post/liked_posts.html', context)


# ------------------------------
# ฟังก์ชัน: แสดงกิจกรรมที่บันทึกไว้
# ------------------------------
@login_required
def saved_posts_view(request):
    saved_posts = request.user.saved_posts.filter(
        is_hidden=False,
        is_deleted=False,
    ).order_by('-created_at')
    context = {'posts': saved_posts, 'title': 'กิจกรรมที่บันทึกไว้ '}
    return render(request, 'post/saved_posts.html', context)


# ------------------------------
# ฟังก์ชัน: แผนที่กิจกรรม
# ------------------------------
@login_required
def map_overview(request):
    posts = Post.objects.filter(
        status=Post.Status.APPROVED,
        is_hidden=False,
        is_deleted=False,
        map_lat__isnull=False,
        map_lng__isnull=False,
    )

    events = []
    for p in posts:
        try:
            lat = float(p.map_lat)
            lng = float(p.map_lng)
        except (TypeError, ValueError):
            continue

        events.append({
            "id": p.id,
            "title": p.title,
            "lat": lat,
            "lng": lng,
            "location": p.location or "",
            "date": p.event_date.strftime("%d %b %Y") if p.event_date else "",
        })

    context = {
        "events_json": json.dumps(events, cls=DjangoJSONEncoder, ensure_ascii=False),
        "enable_geolocation": True,
    }
    return render(request, "home/map.html", context)
