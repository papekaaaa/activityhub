from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    # specific profile actions (must come before the <str:email> catch-all)
    # ✅ เพิ่ม: ลบบัญชีตัวเอง
    path('profile/delete-account/', views.delete_account_confirm_view, name='delete_account_confirm'),

    # ✅ เพิ่ม: เปลี่ยนรหัสผ่าน (ยืนยัน 2 ชั้น)
    path('profile/change-password/', views.password_change_confirm_view, name='password_change_confirm'),
    path('profile/change-password/new/', views.password_change_view, name='password_change'),

    path('profile/<str:email>/', views.profile_detail_view, name='profile_detail'),
    path('profile/<str:email>/follow/', views.follow_toggle_view, name='follow_toggle'),
]
