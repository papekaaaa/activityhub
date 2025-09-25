# approver/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden

# Import models เพื่อใช้ Enum
from post.models import Post
from users.models import User

# --- สร้าง Decorator สำหรับตรวจสอบ Role ---
def roles_required(allowed_roles=[]):
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('login') # หรือหน้า login ของคุณ
            if request.user.role not in allowed_roles:
                return HttpResponseForbidden("คุณไม่มีสิทธิ์เข้าถึงหน้านี้")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator
# -----------------------------------------

@login_required
@roles_required(allowed_roles=[User.Role.APPROVER, User.Role.ADMIN])
def approver_dashboard(request):
    # ใช้ Enum จาก Model แทนการใช้ String 'PENDING'
    pending_posts = Post.objects.filter(status=Post.Status.PENDING)
    
    context = {
        'pending_posts': pending_posts
    }
    return render(request, 'approver/dashboard.html', context)


# (ต่อจากโค้ดด้านบนในไฟล์เดียวกัน)

@login_required
@roles_required(allowed_roles=[User.Role.APPROVER, User.Role.ADMIN])
def approve_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        post.status = Post.Status.APPROVED
        post.save()
        messages.success(request, f"อนุมัติโพสต์ '{post.title}' เรียบร้อยแล้ว")
    return redirect('approver_dashboard')

@login_required
@roles_required(allowed_roles=[User.Role.APPROVER, User.Role.ADMIN])
def reject_post(request, post_id):
    if request.method == 'POST':
        post = get_object_or_404(Post, id=post_id)
        post.status = Post.Status.REJECTED
        post.save()
        messages.warning(request, f"ปฏิเสธโพสต์ '{post.title}' เรียบร้อยแล้ว")
    return redirect('approver_dashboard')