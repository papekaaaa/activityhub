# approver/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden
from django.urls import reverse

from post.models import Post
from users.models import User


# --- Decorator ตรวจสอบ Role ---
def roles_required(allowed_roles=None):
    if allowed_roles is None:
        allowed_roles = []

    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect("login")  # หน้า login ของโปรเจกต์
            if allowed_roles and request.user.role not in allowed_roles:
                return HttpResponseForbidden("คุณไม่มีสิทธิ์เข้าถึงหน้านี้")
            return view_func(request, *args, **kwargs)

        return _wrapped_view

    return decorator


# -----------------------------
# แดชบอร์ดสำหรับ Approver / Admin
# -----------------------------
@login_required
@roles_required(allowed_roles=[User.Role.APPROVER, User.Role.ADMIN])
def approver_dashboard(request):
    """
    main_tab: manage / approve
    sub_tab:  accounts / posts / reports   (ใช้เฉพาะตอน main_tab = manage)
    """

    main_tab = request.GET.get("main", "manage")  # ค่าเริ่มต้น = จัดการบัญชี
    sub_tab = request.GET.get("sub", "accounts")  # ค่าเริ่มต้น = แท็บบัญชี

    # ข้อมูลผู้ใช้ทั้งหมด (ใช้ในแท็บ "บัญชี")
    accounts = User.objects.all().order_by("date_joined")

    # โพสต์ทั้งหมด (ใช้ในแท็บ "โพสต์")
    all_posts = (
        Post.objects.select_related("organizer")
        .all()
        .order_by("-created_at")
    )

    # โพสต์ที่รออนุมัติ (ใช้ในหัวข้อ "ยืนยันโพสต์")
    pending_posts = (
        Post.objects.select_related("organizer")
        .filter(status=Post.Status.PENDING)
        .order_by("-created_at")
    )

    # TODO: ถ้ามี Model รายงานจริง ให้ดึงมาแทน list ว่างพวกนี้
    post_reports = []  # รายงานโพสต์
    user_reports = []  # รายงานบัญชี

    context = {
        "main_tab": main_tab,
        "sub_tab": sub_tab,
        "accounts": accounts,
        "all_posts": all_posts,
        "pending_posts": pending_posts,
        "post_reports": post_reports,
        "user_reports": user_reports,
    }
    return render(request, "approver/dashboard.html", context)


# -----------------------------
# อนุมัติ / ปฏิเสธ โพสต์
# -----------------------------
@login_required
@roles_required(allowed_roles=[User.Role.APPROVER, User.Role.ADMIN])
def approve_post(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        post.status = Post.Status.APPROVED
        post.save()
        messages.success(request, f"อนุมัติโพสต์ '{post.title}' เรียบร้อยแล้ว")
    # กลับไปที่แท็บ "ยืนยันโพสต์"
    return redirect(f"{reverse('approver_dashboard')}?main=approve")


@login_required
@roles_required(allowed_roles=[User.Role.APPROVER, User.Role.ADMIN])
def reject_post(request, post_id):
    if request.method == "POST":
        post = get_object_or_404(Post, id=post_id)
        post.status = Post.Status.REJECTED
        post.save()
        messages.warning(request, f"ปฏิเสธโพสต์ '{post.title}' เรียบร้อยแล้ว")
    # กลับไปที่แท็บ "ยืนยันโพสต์"
    return redirect(f"{reverse('approver_dashboard')}?main=approve")
