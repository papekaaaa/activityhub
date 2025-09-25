from django.urls import path
from . import views

# เปลี่ยนชื่อ view หลักของคุณเป็น approver_dashboard เพื่อให้สอดคล้องกัน
urlpatterns = [
    path('', views.approver_dashboard, name='approver_dashboard'),
    path('post/<int:post_id>/approve/', views.approve_post, name='approve_post'),
    path('post/<int:post_id>/reject/', views.reject_post, name='reject_post'),
]