from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from .forms import UserUpdateForm, ProfileUpdateForm
from .models import Profile, User
from post.models import Post
from activity_register.models import ActivityRegistration   # ✅ เพิ่มบรรทัดนี้


@login_required
def profile_view(request):
    user_posts = Post.objects.filter(
        organizer=request.user
    ).order_by('-created_at')
    profile = request.user.profile

    # ✅ กิจกรรมที่เคยลงทะเบียน
    registrations = ActivityRegistration.objects.filter(
        user=request.user
    ).select_related('post').order_by('-id')

    context = {
        'user_posts': user_posts,
        'profile': profile,
        'followers_count': profile.followers_count(),
        'following_count': profile.following_count(),
        'registrations': registrations,   # ✅ ส่งไปหน้า template
    }
    return render(request, 'users/profile.html', context)


@login_required
def profile_edit_view(request):
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = ProfileUpdateForm(
            request.POST,
            request.FILES,
            instance=request.user.profile
        )
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'โปรไฟล์ของคุณได้รับการอัปเดตเรียบร้อยแล้ว!')
            return redirect('profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = ProfileUpdateForm(instance=request.user.profile)

    return render(request, 'users/profile_edit.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })


# ✅ โปรไฟล์ของผู้ใช้อื่น
@login_required
def profile_detail_view(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
    profile = target_user.profile
    posts = Post.objects.filter(organizer=target_user, status=Post.Status.APPROVED)
    is_following = request.user.profile in profile.followers.all()

    context = {
        'target_user': target_user,
        'profile': profile,
        'posts': posts,
        'is_following': is_following,
        'followers_count': profile.followers_count(),
        'following_count': profile.following_count(),
    }
    return render(request, 'users/profile_detail.html', context)


# ✅ ปุ่มติดตาม / เลิกติดตาม (ใช้ได้ทั้ง form ปกติ + AJAX)
@login_required
def follow_toggle_view(request, user_id):
    target_user = get_object_or_404(User, id=user_id)
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
