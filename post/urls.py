
# from django.urls import path
# from . import views

# urlpatterns = [
#     path('create/', views.create_post, name='create_post'),
#     path('<int:post_id>/edit/', views.post_update_view, name='post_edit'),
#     path('<int:post_id>/delete/', views.post_delete_view, name='post_delete'),
# ]

# from django.urls import path
# from . import views

# urlpatterns = [
#     path('create/', views.create_post, name='create_post'),
# ]

# from django.urls import path
# from . import views

# urlpatterns = [
#     path('create/', views.create_post, name='create_post'),
#     path('<int:post_id>/edit/', views.post_update_view, name='post_update'),
#     path('<int:post_id>/delete/', views.post_delete_view, name='post_delete'),
#     path('<int:post_id>/', views.post_detail_view, name='post_detail'),
# ]

from django.urls import path
from . import views

app_name = 'post'  # ✅ เพิ่มเพื่อใช้ namespace 'post:...'

urlpatterns = [

    path('create/', views.create_post, name='create_post'),
    path('<int:post_id>/', views.post_detail_view, name='post_detail'),
    path('<int:post_id>/edit/', views.post_update_view, name='post_edit'),
    path('<int:post_id>/delete/', views.post_delete_view, name='post_delete'),
]

