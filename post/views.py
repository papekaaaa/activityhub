
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import HttpResponseForbidden # Import เพิ่ม
from .models import Post # Import เพิ่ม
from .forms import PostForm

@login_required # บังคับให้ต้องล็อกอินก่อนเสมอ
def create_post(request):
    if request.method == 'POST':
        # รับข้อมูลจากฟอร์มที่ส่งมา
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            # ยังไม่บันทึกลง DB จริง เพื่อกำหนดค่า organizer
            post = form.save(commit=False) 
            # กำหนดให้ organizer คือ user ที่ล็อกอินอยู่
            post.organizer = request.user 
            post.save() # บันทึกข้อมูลลงฐานข้อมูล
            
            messages.success(request, 'สร้างกิจกรรมของคุณเรียบร้อยแล้ว และได้ส่งไปเพื่อรอการอนุมัติ')
            return redirect('profile') # กลับไปที่หน้าโปรไฟล์
    else:
        # ถ้าเป็น GET request ให้แสดงฟอร์มว่างๆ
        form = PostForm()

    context = {
        'form': form,
        'title': 'สร้างกิจกรรมใหม่' # ส่ง title ไปให้ template
    }
    # เราจะใช้ template ชื่อ post_form.html
    return render(request, 'post/post_form.html', context)

@login_required
def post_update_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    # ตรวจสอบสิทธิ์: เฉพาะเจ้าของโพสต์เท่านั้นที่แก้ไขได้
    if post.organizer != request.user:
        return HttpResponseForbidden("คุณไม่มีสิทธิ์แก้ไขกิจกรรมนี้")

    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            messages.success(request, 'กิจกรรมของคุณได้รับการอัปเดตแล้ว!')
            return redirect('post_detail', post_id=post.id)
    else:
        form = PostForm(instance=post)

    context = {
        'form': form,
        'title': 'แก้ไขกิจกรรม' # ส่ง title ไปให้ template
    }
    return render(request, 'post/post_form.html', context)


@login_required
def post_delete_view(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    # ตรวจสอบสิทธิ์: เฉพาะเจ้าของโพสต์เท่านั้นที่ลบได้
    if post.organizer != request.user:
        return HttpResponseForbidden("คุณไม่มีสิทธิ์ลบกิจกรรมนี้")

    if request.method == 'POST':
        post.delete()
        messages.success(request, 'กิจกรรมของคุณถูกลบเรียบร้อยแล้ว')
        return redirect('profile') # กลับไปหน้าโปรไฟล์

    context = {
        'post': post
    }
    return render(request, 'post/post_confirm_delete.html', context)