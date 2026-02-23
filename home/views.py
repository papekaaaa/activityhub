from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.core.serializers.json import DjangoJSONEncoder
from django.db.models import Avg, Q, Count, Exists, OuterRef, Value, BooleanField
from post.models import Post
from activity_register.models import ActivityReview, ActivityRegistration
from chat.models import ChatRoom
import json
from django.contrib.auth import get_user_model
from users.models import Profile  # ✅ เพิ่มเพื่อเช็คสถานะติดตาม


def index_view(request):
    if request.user.is_authenticated:
        return redirect('home:home')
    return render(request, 'home/index.html')


def map_view(request):
    return render(request, 'home/map.html')


def about_view(request):
    return render(request, 'home/about.html')


def about(request):
    User = get_user_model()

    volunteer_count = User.objects.filter(is_active=True).count()

    total_posts_count = Post.objects.filter(
        is_deleted=False,
        is_hidden=False,
        status=Post.Status.APPROVED
    ).count()

    context = {
        "volunteer_count": f"{volunteer_count:,}",
        "total_posts_count": f"{total_posts_count:,}",
    }
    return render(request, "home/about.html", context)


def home_view(request):
    """
    หน้า feed หลัก
    - รองรับการกรองตามหมวดหมู่ (category)
    - รองรับการค้นหา (search) ตามชื่อกิจกรรม / รายละเอียด / สถานที่ / ชื่อผู้จัด
    """
    posts = Post.objects.filter(
        status=Post.Status.APPROVED,
        is_hidden=False,
        is_deleted=False,
    )

    # ✅ จำนวนรีวิวต่อโพสต์ (reverse name = activity_reviews)
    posts = posts.annotate(review_count=Count('activity_reviews', distinct=True))

    # ✅ สถานะติดตาม (เชื่อมกับ Profile.followers)
    if request.user.is_authenticated:
        my_profile = getattr(request.user, "profile", None)
        if my_profile:
            follow_qs = Profile.objects.filter(
                user_id=OuterRef('organizer_id'),
                followers=my_profile
            )
            posts = posts.annotate(is_following=Exists(follow_qs))
        else:
            posts = posts.annotate(is_following=Value(False, output_field=BooleanField()))
    else:
        posts = posts.annotate(is_following=Value(False, output_field=BooleanField()))

    categories = [c[0] for c in Post.CATEGORY_CHOICES]

    selected_category = request.GET.get('category')
    search_query = request.GET.get('search', '').strip()

    if selected_category:
        posts = posts.filter(category=selected_category)

    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(description__icontains=search_query) |
            Q(location__icontains=search_query) |
            Q(organizer__first_name__icontains=search_query) |
            Q(organizer__last_name__icontains=search_query)
        ).distinct()

    posts = posts.order_by('-created_at')

    context = {
        'posts': posts,
        'categories': categories,
        'selected_category': selected_category,
        'search_query': search_query,
    }
    return render(request, 'home/homes.html', context)


def category_view(request):
    category_type = request.GET.get('type')

    posts = Post.objects.filter(
        status=Post.Status.APPROVED,
        is_hidden=False,
        is_deleted=False,
    )

    # ✅ จำนวนรีวิวต่อโพสต์
    posts = posts.annotate(review_count=Count('activity_reviews', distinct=True))

    # ✅ สถานะติดตาม
    if request.user.is_authenticated:
        my_profile = getattr(request.user, "profile", None)
        if my_profile:
            follow_qs = Profile.objects.filter(
                user_id=OuterRef('organizer_id'),
                followers=my_profile
            )
            posts = posts.annotate(is_following=Exists(follow_qs))
        else:
            posts = posts.annotate(is_following=Value(False, output_field=BooleanField()))
    else:
        posts = posts.annotate(is_following=Value(False, output_field=BooleanField()))

    posts = posts.order_by('-created_at')

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
    post = get_object_or_404(
        Post,
        id=post_id,
        status=Post.Status.APPROVED,
        is_hidden=False,
        is_deleted=False,
    )

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

    # ✅ ดึงสถานะลงทะเบียนของ user (ถ้ามี)
    my_reg = None
    if request.user.is_authenticated:
        my_reg = ActivityRegistration.objects.filter(
            user=request.user,
            post=post,
        ).first()

        if my_reg and my_reg.status == ActivityRegistration.Status.CANCEL_PENDING:
            my_reg.finalize_cancel_if_expired()
            my_reg.refresh_from_db()

    has_chat_room = ChatRoom.objects.filter(post=post).exists()

    user_is_registered = False
    if my_reg and my_reg.status == 'ACTIVE':
        user_is_registered = True

    context = {
        'post': post,
        'reviews': reviews,
        'review_count': review_count,
        'avg_rating': avg_rating,
        'avg_rating_int': avg_rating_int,
        'my_reg': my_reg,
        'active_reg_count': post.active_registrations_count(),
        'is_full': post.is_full(),
        'has_chat_room': has_chat_room,
        'user_is_registered': user_is_registered,
        'cancel_undo_until_iso': my_reg.cancel_undo_until.isoformat() if my_reg and my_reg.cancel_undo_until else '',
        'cooldown_until_iso': my_reg.cooldown_until.isoformat() if my_reg and my_reg.cooldown_until and my_reg.status == 'CANCELED' else '',
    }
    return render(request, 'home/post_detail.html', context)


def _get_events_from_posts():
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
    return events


def public_map_view(request):
    events = _get_events_from_posts()

    context = {
        "events_json": json.dumps(events, cls=DjangoJSONEncoder, ensure_ascii=False),
        "enable_geolocation": False,
    }
    return render(request, "home/map.html", context)


@login_required
def nearby_map_view(request):
    events = _get_events_from_posts()

    context = {
        "events_json": json.dumps(events, cls=DjangoJSONEncoder, ensure_ascii=False),
        "radius_km": 30,
    }
    return render(request, "home/map_nearby.html", context)
