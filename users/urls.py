from django.urls import path
from . import views

urlpatterns = [
    path('profile/', views.profile_view, name='profile'),
    path('profile/edit/', views.profile_edit_view, name='profile_edit'),
    path('profile/<int:user_id>/', views.profile_detail_view, name='profile_detail'),
    path('profile/<int:user_id>/follow/', views.follow_toggle_view, name='follow_toggle'),
]
