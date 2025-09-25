from django.urls import path
from . import views

urlpatterns = [
    # /user/profile/ -> หน้าแสดงโปรไฟล์หลัก
    path('profile/', views.profile_view, name='profile'),
    
    # /user/profile/edit/ -> หน้าสำหรับแก้ไขโปรไฟล์
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
]