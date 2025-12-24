from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden, JsonResponse
from django.views.decorators.http import require_POST
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Avg
from .models import Post
from .forms import PostForm
from activity_register.models import ActivityReview
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

            # สร้างห้องแชทของกิจกรรม + ดึง organizer เข้าห้อง
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

    # ดึง url รูปโปรไฟล์ของ user
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
            post = form.save(commit=False)
            post.map_lat = request.POST.get('map_lat') or None
            post.map_lng = request.POST.get('map_lng') or None
            post.save()
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

    reviews = (
        post.activity_reviews
        .select_related('user')
        .order_by('-created_at')
    )

    avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
    avg_rating_int = int(round(avg_rating)) if avg_rating else 0
    review_count = reviews.count()

    context = {
        'post': post,
        'reviews': reviews,
        'avg_rating': avg_rating,
        'avg_rating_int': avg_rating_int,
        'review_count': review_count,
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
    # ✅ ไม่แสดงโพสต์ที่ถูกซ่อน/ลบแล้ว
    liked_posts = request.user.liked_posts.filter(
        is_hidden=False,
        is_deleted=False,
    ).order_by('-created_at')
    context = {'posts': liked_posts, 'title': 'กิจกรรมที่กดถูกใจ ❤️'}
    return render(request, 'post/liked_posts.html', context)


# ------------------------------
# ฟังก์ชัน: แสดงกิจกรรมที่บันทึกไว้
# ------------------------------
@login_required
def saved_posts_view(request):
    # ✅ ไม่แสดงโพสต์ที่ถูกซ่อน/ลบแล้ว
    saved_posts = request.user.saved_posts.filter(
        is_hidden=False,
        is_deleted=False,
    ).order_by('-created_at')
    context = {'posts': saved_posts, 'title': 'กิจกรรมที่บันทึกไว้ 🔖'}
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
