
from django.urls import path
from . import views

app_name = "activity_register"

urlpatterns = [
    # สมัครกิจกรรม
    path("register/<int:post_id>/", views.register_activity, name="register_activity"),

    # แก้ไขข้อมูลโปรไฟล์ที่ใช้สมัครกิจกรรม
    path("profile/edit/", views.edit_register_profile, name="edit_register_profile"),

    # ใหม่: กิจกรรมที่เคยเข้าร่วม + รีวิว
    # กิจกรรมที่เคยเข้าร่วม
    path("joined/", views.joined_activities, name="joined_activities"),

    # รีวิวกิจกรรม
    path("review/<int:post_id>/", views.review_activity, name="review_activity"),
]
