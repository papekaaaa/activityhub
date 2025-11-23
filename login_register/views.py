from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib import messages

from users.models import User
from .forms import CustomUserCreationForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect('home:home')

    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)

            messages.success(
                request,
                f"สมัครสมาชิกสำเร็จ ยินดีต้อนรับ, {user.email}!"
            )

            return redirect('home:home')
    else:
        form = CustomUserCreationForm()

    return render(request, 'login/register.html', {'form': form})


def login_view(request):
    if request.user.is_authenticated:
        return redirect('home:home')

    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            email = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')

            # ถ้ามี custom backend ที่ใช้ email ให้ส่ง email ตามนี้
            user = authenticate(email=email, password=password)

            if user is not None:
                login(request, user)

                if user.role == User.Role.ADMIN:
                    messages.success(request, f"ยินดีต้อนรับ Admin, {user.email}")
                    return redirect('admin:index')

                elif user.role == User.Role.APPROVER:
                    messages.success(request, "เข้าสู่ระบบสำหรับ Approver สำเร็จ")
                    return redirect('approver_dashboard')

                else:
                    messages.success(request, "เข้าสู่ระบบสำเร็จ")
                    return redirect('home:home')
            else:
                messages.error(request, "อีเมลหรือรหัสผ่านไม่ถูกต้อง")
        else:
            messages.error(request, "อีเมลหรือรหัสผ่านไม่ถูกต้อง")
    else:
        form = AuthenticationForm()

    return render(request, 'login/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, "คุณออกจากระบบสำเร็จแล้ว")
    return redirect('home:home')
