from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib.auth import logout  # ✅ เพิ่ม
from django.db import transaction  # ✅ เพิ่ม
from django.contrib.auth.forms import SetPasswordForm
from django.contrib.auth import update_session_auth_hash  # ✅ เพิ่ม (เพราะมีใช้ด้านล่าง)

from .forms import UserUpdateForm, ProfileUpdateForm
from .forms import DeleteAccountForm  # ✅ เพิ่ม (ไม่ลบของเดิม)
from .models import Profile, User
from post.models import Post
from activity_register.models import ActivityRegistration


@login_required
def profile_view(request):
    """
    โปรไฟล์ของตัวเอง
    - โพสต์ที่เราเป็น organizer
    - กิจกรรมที่เราเคยลงทะเบียน
    """
    # ✅ ถ้าบัญชีถูก soft delete แล้ว ให้เด้งออกทันที (กันข้อมูลโผล่)
    if getattr(request.user, "is_deleted", False):
        logout(request)
        return redirect('home:index')

    user_posts = Post.objects.filter(
        organizer=request.user,
        is_deleted=False,
        is_hidden=False
    ).order_by('-created_at')

    profile = request.user.profile

    registrations = ActivityRegistration.objects.filter(
        user=request.user
    ).select_related('post').order_by('-id')

    context = {
        'user_posts': user_posts,
        'profile': profile,
        'followers_count': profile.followers_count(),
        'following_count': profile.following_count(),
        'registrations': registrations,
    }
    return render(request, 'users/profile.html', context)


@login_required
def profile_edit_view(request):
    profile = request.user.profile

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=profile
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'โปรไฟล์ของคุณได้รับการอัปเดตเรียบร้อยแล้ว!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=profile)

    return render(
        request,
        'users/profile_edit.html',
        {
            'user_form': user_form,
            'profile_form': profile_form,
        },
    )


@login_required
def profile_detail_view(request, user_id):
    # ✅ ถ้ากดส่องโปรไฟล์แล้วเป็น "ตัวเอง" ให้ไปหน้าโปรไฟล์ตัวเองทันที
    if request.user.id == user_id:
        return redirect('profile')

    # ✅ ไม่ให้ดูโปรไฟล์ของ user ที่ถูกลบ (ซ่อน)
    target_user = get_object_or_404(User, id=user_id, is_deleted=False, is_active=True)
    profile = target_user.profile

    posts = Post.objects.filter(
        organizer=target_user,
        status=Post.Status.APPROVED,
        is_deleted=False,
        is_hidden=False
    ).order_by('-created_at')

    registrations = ActivityRegistration.objects.filter(
        user=target_user
    ).select_related('post').order_by('-post__event_date', '-id')

    is_following = request.user.profile in profile.followers.all()

    context = {
        'target_user': target_user,
        'profile': profile,
        'posts': posts,
        'is_following': is_following,
        'followers_count': profile.followers_count(),
        'following_count': profile.following_count(),
        'registrations': registrations,
    }
    return render(request, 'users/profile_detail.html', context)


@login_required
def follow_toggle_view(request, user_id):
    # ✅ กัน follow บัญชีที่ถูกลบ
    target_user = get_object_or_404(User, id=user_id, is_deleted=False, is_active=True)
    target_profile = target_user.profile
    my_profile = request.user.profile

    if request.method != "POST":
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"error": "POST required"}, status=400)
        return redirect('profile_detail', user_id=user_id)

    is_following = False
    if my_profile != target_profile:
        if my_profile in target_profile.followers.all():
            target_profile.followers.remove(my_profile)
            is_following = False
        else:
            target_profile.followers.add(my_profile)
            is_following = True

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "is_following": is_following,
            "followers_count": target_profile.followers_count(),
        })

    return redirect('profile_detail', user_id=user_id)


# ✅ เพิ่ม: ลบบัญชีตัวเอง (ยืนยัน 2 ชั้น + รหัสผ่าน) + logout ทันที
@login_required
def delete_account_confirm_view(request):
    # ถ้าถูกลบแล้ว ให้ logout ออก
    if getattr(request.user, "is_deleted", False):
        logout(request)
        return redirect('home:index')

    if request.method == "POST":
        form = DeleteAccountForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data["password"]

            # เช็ครหัสผ่านก่อน
            if not request.user.check_password(password):
                form.add_error("password", "รหัสผ่านไม่ถูกต้อง")
            else:
                with transaction.atomic():
                    user = request.user

                    # ✅ ซ่อน/ลบโพสต์ของ user นี้ (กันระบบพัง + ไม่โชว์ในเว็บ)
                    Post.objects.filter(organizer=user).update(is_deleted=True, is_hidden=True)

                    # ✅ soft delete user
                    user.soft_delete()

                # ✅ logout ทันที
                logout(request)
                messages.success(request, "ลบบัญชีเรียบร้อยแล้ว (บัญชีถูกปิดการใช้งานและซ่อนข้อมูล)")
                return redirect('home:index')
    else:
        form = DeleteAccountForm()

    return render(request, "users/delete_account_confirm.html", {"form": form})


@login_required
def password_change_confirm_view(request):
    """
    Step 1: ยืนยันตัวตนด้วยรหัสผ่านปัจจุบัน
    """
    if request.method == "POST":
        current_password = request.POST.get("current_password", "")
        if request.user.check_password(current_password):
            request.session["pwd_change_verified"] = True
            return redirect("password_change")
        messages.error(request, "รหัสผ่านปัจจุบันไม่ถูกต้อง")

    return render(request, "users/password_change_confirm.html")


@login_required
def password_change_view(request):
    """
    Step 2: ตั้งรหัสผ่านใหม่ (หลังผ่าน step 1 แล้วเท่านั้น)
    """
    if not request.session.get("pwd_change_verified"):
        return redirect("password_change_confirm")

    if request.method == "POST":
        form = SetPasswordForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # กันหลุด login
            request.session.pop("pwd_change_verified", None)
            messages.success(request, "เปลี่ยนรหัสผ่านเรียบร้อยแล้ว")
            return redirect("profile")
    else:
        form = SetPasswordForm(request.user)

    return render(request, "users/password_change.html", {"form": form})
