from datetime import date, datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone

from .forms import ActivityRegistrationForm, ActivityReviewForm
from .models import ActivityRegistration, ActivityReview
from post.models import Post


def _serialize_for_session(data: dict) -> dict:
    """
    แปลงค่าใน cleaned_data ให้เก็บใน session ได้
    - ถ้าเป็น date/datetime จะถูกแปลงเป็น string แบบ ISO
    """
    if not isinstance(data, dict):
        return data

    result = {}
    for key, value in data.items():
        if isinstance(value, (date, datetime)):
            result[key] = value.isoformat()
        else:
            result[key] = value
    return result


# -----------------------------
# สมัครกิจกรรม
# -----------------------------
@login_required
def register_activity(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    session_data = request.session.get("register_profile")

    if request.method == "POST":
        form = ActivityRegistrationForm(request.POST)
        if form.is_valid():
            registration = form.save(commit=False)
            registration.user = request.user
            registration.post = post
            registration.save()

            request.session["register_profile"] = _serialize_for_session(
                form.cleaned_data
            )

            messages.success(request, "สมัครเข้าร่วมกิจกรรมเรียบร้อยแล้ว")
            return render(
                request,
                "activity_register/register_form.html",
                {
                    "form": form,
                    "post": post,
                    "success": True,
                    "edit_mode": False,
                },
            )
    else:
        if session_data:
            form = ActivityRegistrationForm(initial=session_data)
        else:
            last_reg = ActivityRegistration.objects.filter(
                user=request.user
            ).order_by("-id").first()
            if last_reg:
                form = ActivityRegistrationForm(instance=last_reg)
            else:
                form = ActivityRegistrationForm()

    return render(
        request,
        "activity_register/register_form.html",
        {
            "form": form,
            "post": post,
            "success": False,
            "edit_mode": False,
        },
    )


# -----------------------------
# แก้ไขโปรไฟล์ข้อมูลสมัครกิจกรรม
# -----------------------------
@login_required
def edit_register_profile(request):
    session_data = request.session.get("register_profile")

    last_reg = None
    if not session_data:
        last_reg = ActivityRegistration.objects.filter(
            user=request.user
        ).order_by("-id").first()

    if request.method == "POST":
        form = ActivityRegistrationForm(request.POST)
        if form.is_valid():
            request.session["register_profile"] = _serialize_for_session(
                form.cleaned_data
            )
            messages.success(
                request,
                "บันทึกข้อมูลสำหรับสมัครกิจกรรมเรียบร้อยแล้ว "
                "ข้อมูลนี้จะถูกกรอกให้อัตโนมัติเมื่อสมัครกิจกรรมครั้งถัดไป",
            )
            return redirect("profile")
    else:
        if session_data:
            form = ActivityRegistrationForm(initial=session_data)
        elif last_reg:
            form = ActivityRegistrationForm(instance=last_reg)
        else:
            form = ActivityRegistrationForm()

    return render(
        request,
        "activity_register/edit_register_profile.html",
        {
            "form": form,
        },
    )


# -----------------------------
# กิจกรรมที่เคยเข้าร่วม
# -----------------------------
@login_required
def joined_activities(request):
    """
    เงื่อนไข: user เคยสมัคร + วันกิจกรรมผ่านไปแล้ว
    """
    now = timezone.now()

    joined_posts = (
        Post.objects.filter(
            registrations__user=request.user,
            event_date__lt=now,
        )
        .distinct()
        .order_by("-event_date")
    )

    user_reviews = ActivityReview.objects.filter(
        user=request.user,
        post__in=joined_posts,
    )
    reviewed_post_ids = {r.post_id for r in user_reviews}

    context = {
        "joined_posts": joined_posts,
        "reviewed_post_ids": reviewed_post_ids,
    }
    return render(request, "activity_register/joined_activities.html", context)


# -----------------------------
# สร้าง/แก้ไข รีวิวกิจกรรม
# -----------------------------
@login_required
def review_activity(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    # ยังไม่ถึงวันกิจกรรม ห้ามรีวิว
    if not post.event_date or post.event_date > timezone.now():
        messages.error(request, "ยังไม่สามารถรีวิวได้ ต้องรอให้กิจกรรมจบก่อน")
        return redirect("activity_register:joined_activities")

    # ต้องเคยลงทะเบียนกิจกรรมนี้
    has_registered = ActivityRegistration.objects.filter(
        post=post,
        user=request.user,
    ).exists()

    if not has_registered:
        messages.error(request, "คุณยังไม่ได้เข้าร่วมกิจกรรมนี้ จึงไม่สามารถรีวิวได้")
        return redirect("activity_register:joined_activities")

    review, created = ActivityReview.objects.get_or_create(
        post=post,
        user=request.user,
    )

    if request.method == "POST":
        form = ActivityReviewForm(request.POST, request.FILES, instance=review)
        if form.is_valid():
            form.save()
            messages.success(request, "บันทึกรีวิวเรียบร้อยแล้ว")
            return redirect("activity_register:joined_activities")
    else:
        form = ActivityReviewForm(instance=review)

    return render(
        request,
        "activity_register/review_form.html",
        {
            "form": form,
            "post": post,
            "is_edit": not created,
        },
    )
