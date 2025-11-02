from django.urls import path
from .views import *

urlpatterns = [
    path('', index_view, name='index'),
    path('home/', home_view, name='home'),
    path('post/<int:post_id>/', post_detail_view, name='post_detail'),
    path('map/', map_view, name='map'),
    path('about/', about_view, name='about'),
    path('category/', category_view, name='category'),
]
