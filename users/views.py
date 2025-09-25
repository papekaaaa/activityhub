# users/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .forms import UserUpdateForm, ProfileUpdateForm
from post.models import Post # Import โมเดล Post

# 1. View สำหรับแสดงหน้าโปรไฟล์และโพสต์ของตัวเอง
@login_required
def profile_view(request):
    # ดึงโพสต์ทั้งหมดที่สร้างโดยผู้ใช้ที่ล็อกอินอยู่
    user_posts = Post.objects.filter(organizer=request.user).order_by('-created_at')
    
    context = {
        'user_posts': user_posts
    }
    return render(request, 'users/profile.html', context)


# 2. View สำหรับหน้า "แก้ไข" โปรไฟล์ (โค้ดเดิมจากรอบที่แล้ว)
@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(request.POST, request.FILES, instance=request.user.profile)

        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'โปรไฟล์ของคุณได้รับการอัปเดตเรียบร้อยแล้ว!')
            return redirect('profile') # กลับไปหน้าโปรไฟล์หลัก

    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    context = {
        'user_form': user_form,
        'profile_form': profile_form
    }
    return render(request, 'users/profile_edit.html', context) # ใช้ template ใหม่