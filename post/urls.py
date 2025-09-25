
from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_post, name='create_post'),
    path('<int:post_id>/edit/', views.post_update_view, name='post_edit'),
    path('<int:post_id>/delete/', views.post_delete_view, name='post_delete'),
]