from django.urls import path
from .views import *
urlpatterns = [
    path('', home_view, name='home'),
    path('post/<int:post_id>/', post_detail_view, name='post_detail'),
    
]