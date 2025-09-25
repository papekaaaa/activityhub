from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import PostForm

@login_required # 1. บังคับให้ต้องล็อกอินก่อนเสมอ
def create_post(request):
    if request.method == 'POST':
        # 2. รับข้อมูลจากฟอร์มที่ส่งมาพร้อมกับไฟล์ภาพ
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            # 3. ยังไม่บันทึกลง DB จริง เพื่อกำหนดค่า organizer ก่อน
            post = form.save(commit=False) 
            # 4. กำหนดให้ organizer คือ user ที่ล็อกอินอยู่ในขณะนั้น
            post.organizer = request.user 
            post.save() # 5. บันทึกข้อมูลลงฐานข้อมูล
            
            messages.success(request, 'สร้างกิจกรรมของคุณเรียบร้อยแล้ว และได้ส่งไปเพื่อรอการอนุมัติ')
            return redirect('home') # 6. กลับไปที่หน้าหลัก
    else:
        # ถ้าเป็น GET request ให้แสดงฟอร์มว่างๆ
        form = PostForm()

    context = {
        'form': form
    }
    return render(request, 'post/create_post.html', context)