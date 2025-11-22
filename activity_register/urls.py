from django.urls import path
from . import views

app_name = 'activity_register'

urlpatterns = [
    path('register/<int:post_id>/', views.register_activity, name='register_activity'),
    path('profile/edit/', views.edit_register_profile, name='edit_register_profile'),

    # ใหม่: กิจกรรมที่เคยเข้าร่วม + รีวิว
    path('joined/', views.joined_activities, name='joined_activities'),
    path('review/<int:post_id>/', views.review_activity, name='review_activity'),
]
