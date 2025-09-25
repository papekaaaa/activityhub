from django.shortcuts import render, redirect
from .forms import CustomUserCreationForm
from django.contrib.auth import login, authenticate , logout
from django.contrib.auth.forms import AuthenticationForm 
from django.contrib import messages
from users.models import User

def register_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            
            # เพิ่มข้อความแจ้งเตือนว่าสมัครสำเร็จ
            messages.success(request, f"สมัครสมาชิกสำเร็จ ยินดีต้อนรับ, {user.email}!")
            
            # การ redirect ไป 'home' ถูกต้องแล้ว เพราะ role เริ่มต้นคือ USER
            return redirect('home')
        else:
            # ถ้าฟอร์มไม่ผ่าน validation (เช่น email ซ้ำ)
            # Django form จะจัดการ error message ให้เอง
            pass 
    else:
        form = CustomUserCreationForm()
        
    return render(request, 'login/register.html', {'form': form})

def login_view(request):
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(email=email, password=password)
            
            if user is not None:
                login(request, user)
                
                # --- ส่วนที่เพิ่มเข้ามา ---
                # 2. ตรวจสอบ role ของ user แล้ว redirect ไปยังหน้าที่เหมาะสม
                if user.role == User.Role.ADMIN:
                    messages.success(request, f"ยินดีต้อนรับ Admin, {user.email}")
                    return redirect('admin:index') # URL name ของหน้า Django Admin
                
                elif user.role == User.Role.APPROVER:
                    messages.success(request, f"เข้าสู่ระบบสำหรับ Approver สำเร็จ")
                    # *** แก้ 'approver_home' เป็น URL name จริงของคุณใน approver/urls.py ***
                    return redirect('approver_dashboard') 
                
                else: # user.role == User.Role.USER หรือค่าอื่นๆ
                    messages.success(request, "เข้าสู่ระบบสำเร็จ")
                    return redirect('home')
                # --- จบส่วนที่เพิ่มเข้ามา ---

            else:
                messages.error(request, "อีเมลหรือรหัสผ่านไม่ถูกต้อง")
        else:
            messages.error(request, "อีเมลหรือรหัสผ่านไม่ถูกต้อง")
    else:
        form = AuthenticationForm()
        
    return render(request, 'login/login.html', {'form': form})



def logout_view(request):
    # 1. เรียกใช้ฟังก์ชัน logout ของ Django เพื่อเคลียร์ session ของ user
    logout(request)
    
    # (ทางเลือก) เพิ่มข้อความแจ้งเตือนว่าออกจากระบบสำเร็จแล้ว
    messages.success(request, "คุณออกจากระบบสำเร็จแล้ว")
    
    # 2. ส่งผู้ใช้กลับไปยังหน้า login
    return redirect('home')

