from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Avg
from post.models import Post
from activity_register.models import ActivityReview
import json


def index_view(request):
    if request.user.is_authenticated:
        return redirect('home:home')
    return render(request, 'home/index.html')


def map_view(request):
    # หน้านี้ถ้าไม่ได้ใช้แล้ว สามารถลบได้ แต่ยังคงไว้เผื่อเรียกจากที่อื่น
    return render(request, 'home/map.html')


def about_view(request):
    return render(request, 'home/about.html')


def home_view(request):
    posts = Post.objects.filter(status=Post.Status.APPROVED).order_by('-event_date')
    categories = [c[0] for c in Post.CATEGORY_CHOICES]
    selected_category = request.GET.get('category')

    if selected_category:
        posts = posts.filter(category=selected_category)

    context = {
        'posts': posts,
        'categories': categories,
        'selected_category': selected_category,
    }
    return render(request, 'home/homes.html', context)


def category_view(request):
    category_type = request.GET.get('type')
    posts = Post.objects.filter(status=Post.Status.APPROVED)
    if category_type:
        posts = posts.filter(category=category_type)

    context = {
        'posts': posts,
        'selected_category': category_type,
    }
    return render(request, 'home/category.html', context)


@login_required
def post_detail_view(request, post_id):
    """
    รายละเอียดกิจกรรม (หน้า home) + สรุปรีวิวเหมือนหน้าใน app post
    """
    post = get_object_or_404(Post, id=post_id)

    reviews = (
        ActivityReview.objects
        .filter(post=post)
        .select_related('user')
        .order_by('-created_at')
    )

    review_count = reviews.count()
    avg_rating = 0
    avg_rating_int = 0

    if review_count > 0:
        avg_rating = reviews.aggregate(avg=Avg('rating'))['avg'] or 0
        avg_rating_int = int(round(avg_rating))

    context = {
        'post': post,
        'reviews': reviews,
        'review_count': review_count,
        'avg_rating': avg_rating,
        'avg_rating_int': avg_rating_int,
    }
    return render(request, 'home/post_detail.html', context)


# ---------------- MAP HELPERS ----------------

def _get_events_from_posts():
    """
    ดึงโพสต์ที่มีพิกัด map_lat / map_lng และแปลงเป็น list ของ dict
    สำหรับส่งไปใช้ใน JavaScript
    """
    posts = Post.objects.filter(
        status=Post.Status.APPROVED,
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
    return events


def public_map_view(request):
    """
    แผนที่กิจกรรม (หน้า public ก่อนล็อกอิน)
    - แสดงหมุดทุกกิจกรรมที่มีพิกัด
    - ไม่ใช้ geolocation, ดูได้อย่างเดียว
    """
    events = _get_events_from_posts()

    context = {
        "events_json": json.dumps(events, cls=DjangoJSONEncoder, ensure_ascii=False),
        "enable_geolocation": False,  # หน้า public ไม่ใช้ geolocation
    }
    return render(request, "home/map.html", context)


@login_required
def nearby_map_view(request):
    """
    แผนที่กิจกรรมใกล้ตัว (ต้องล็อกอิน)
    - ใช้ geolocation จาก browser
    - filter เฉพาะกิจกรรมในรัศมี ~30km ที่ฝั่ง JS
    """
    events = _get_events_from_posts()

    context = {
        "events_json": json.dumps(events, cls=DjangoJSONEncoder, ensure_ascii=False),
        "radius_km": 30,
    }
    return render(request, "home/map_nearby.html", context)
