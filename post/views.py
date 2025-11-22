
# from django.shortcuts import render, redirect, get_object_or_404
# from django.contrib.auth.decorators import login_required
# from django.contrib import messages
# from django.http import HttpResponseForbidden # Import เพิ่ม
# from .models import Post # Import เพิ่ม
# from .forms import PostForm

# @login_required # บังคับให้ต้องล็อกอินก่อนเสมอ
# def create_post(request):
#     if request.method == 'POST':
#         # รับข้อมูลจากฟอร์มที่ส่งมา
#         form = PostForm(request.POST, request.FILES)
#         if form.is_valid():
#             # ยังไม่บันทึกลง DB จริง เพื่อกำหนดค่า organizer
#             post = form.save(commit=False) 
#             # กำหนดให้ organizer คือ user ที่ล็อกอินอยู่
#             post.organizer = request.user 
#             post.save() # บันทึกข้อมูลลงฐานข้อมูล
            
#             messages.success(request, 'สร้างกิจกรรมของคุณเรียบร้อยแล้ว และได้ส่งไปเพื่อรอการอนุมัติ')
#             return redirect('profile') # กลับไปที่หน้าโปรไฟล์
#     else:
#         # ถ้าเป็น GET request ให้แสดงฟอร์มว่างๆ
#         form = PostForm()

#     context = {
#         'form': form,
#         'title': 'สร้างกิจกรรมใหม่' # ส่ง title ไปให้ template
#     }
#     # เราจะใช้ template ชื่อ post_form.html
#     return render(request, 'post/post_form.html', context)

# @login_required
# def post_update_view(request, post_id):
#     post = get_object_or_404(Post, id=post_id)
#     # ตรวจสอบสิทธิ์: เฉพาะเจ้าของโพสต์เท่านั้นที่แก้ไขได้
#     if post.organizer != request.user:
#         return HttpResponseForbidden("คุณไม่มีสิทธิ์แก้ไขกิจกรรมนี้")

#     if request.method == 'POST':
#         form = PostForm(request.POST, request.FILES, instance=post)
#         if form.is_valid():
#             form.save()
#             messages.success(request, 'กิจกรรมของคุณได้รับการอัปเดตแล้ว!')
#             return redirect('post_detail', post_id=post.id)
#     else:
#         form = PostForm(instance=post)

#     context = {
#         'form': form,
#         'title': 'แก้ไขกิจกรรม' # ส่ง title ไปให้ template
#     }
#     return render(request, 'post/post_form.html', context)


# @login_required
# def post_delete_view(request, post_id):
#     post = get_object_or_404(Post, id=post_id)
#     # ตรวจสอบสิทธิ์: เฉพาะเจ้าของโพสต์เท่านั้นที่ลบได้
#     if post.organizer != request.user:
#         return HttpResponseForbidden("คุณไม่มีสิทธิ์ลบกิจกรรมนี้")

#     if request.method == 'POST':
#         post.delete()
#         messages.success(request, 'กิจกรรมของคุณถูกลบเรียบร้อยแล้ว')
#         return redirect('profile') # กลับไปหน้าโปรไฟล์

#     context = {
#         'post': post
#     }
#     return render(request, 'post/post_confirm_delete.html', context)

# from django.shortcuts import render, redirect
# from django.contrib.auth.decorators import login_required
# from .forms import PostForm

# @login_required
# def create_post(request):
#     if request.method == 'POST':
#         form = PostForm(request.POST, request.FILES)
#         if form.is_valid():
#             post = form.save(commit=False)
#             post.created_by = request.user
#             post.save()
#             return redirect('home')  # เปลี่ยนตามชื่อหน้า home ของคุณ
#     else:
#         form = PostForm()
#     return render(request, 'post/create_post.html', {'form': form})


# def create_post(request):
#     if request.method == 'POST':
#         form = PostForm(request.POST, request.FILES)
#         if form.is_valid():
#             post = form.save(commit=False)
#             post.organizer = request.user
#             post.save()
#             messages.success(request, 'สร้างกิจกรรมของคุณเรียบร้อยแล้ว และได้ส่งไปเพื่อรอการอนุมัติ')
#             return redirect('profile')
#     else:
#         form = PostForm()

#     context = {'form': form, 'title': 'สร้างกิจกรรมใหม่'}
#     return render(request, 'post/post_form.html', context)

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
            post.map_lat = request.POST.get('map_lat')
            post.map_lng = request.POST.get('map_lng')
            post.save()
            messages.success(request, 'สร้างกิจกรรมสำเร็จ! รอการอนุมัติจากผู้ดูแลระบบ')
            return redirect('home:home')
    else:
        form = PostForm()

    # ดึง url รูปโปรไฟล์ของ user
    profile_pic_url = None
    user = request.user

    # กรณีมีโมเดล Profile แยก เช่น user.profile.profile_picture
    if hasattr(user, "profile") and getattr(user.profile, "profile_picture", None):
        if user.profile.profile_picture:
            profile_pic_url = user.profile.profile_picture.url

    # ถ้าเก็บรูปไว้บน User โดยตรง เช่น user.profile_picture
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

            # อัปเดตพิกัดจากฟอร์มเหมือนตอนสร้างโพสต์
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
# ฟังก์ชัน: แสดงรายละเอียดกิจกรรม + รีวิว
# ------------------------------
def post_detail_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # ดึงรีวิวทั้งหมดของโพสต์นี้
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
    liked_posts = request.user.liked_posts.all().order_by('-created_at')
    context = {'posts': liked_posts, 'title': 'กิจกรรมที่กดถูกใจ ❤️'}
    return render(request, 'post/liked_posts.html', context)


# ------------------------------
# ฟังก์ชัน: แสดงกิจกรรมที่บันทึกไว้
# ------------------------------
@login_required
def saved_posts_view(request):
    saved_posts = request.user.saved_posts.all().order_by('-created_at')
    context = {'posts': saved_posts, 'title': 'กิจกรรมที่บันทึกไว้ 🔖'}
    return render(request, 'post/saved_posts.html', context)


# ------------------------------
# ฟังก์ชัน: แสดงทุกกิจกรรมบนแผนที่
# ------------------------------
@login_required
def map_overview(request):
    """
    แผนที่กิจกรรม (สำหรับผู้ใช้ที่ล็อกอิน)
    - แสดงหมุดทุกกิจกรรมที่มีพิกัด
    - ใช้ geolocation แสดงตำแหน่งปัจจุบันของผู้ใช้
    """
    posts = Post.objects.filter(
        status=Post.Status.APPROVED,
        latitude__isnull=False,
        longitude__isnull=False,
    )

    events = []
    for p in posts:
        events.append({
            "id": p.id,
            "title": p.title,
            "lat": float(p.latitude),
            "lng": float(p.longitude),
            "location": p.location or "",
            "date": p.event_date.strftime("%d %b %Y") if p.event_date else "",
        })

    context = {
        "events_json": json.dumps(events, cls=DjangoJSONEncoder, ensure_ascii=False),
        "enable_geolocation": True,
    }
    return render(request, "home/map.html", context)
