from django.urls import path
from . import views

app_name = 'home'

urlpatterns = [
    path('', views.index_view, name='index'),
    path('home/', views.home_view, name='home'),
    path('post/<int:post_id>/', views.post_detail_view, name='post_detail'),

    # แผนที่รวมทุกกิจกรรม (ดูอย่างเดียว – ใช้ในเมนูก่อนล็อกอิน)
    path('map/', views.public_map_view, name='map'),

    # แผนที่กิจกรรมใกล้ตัว (ต้องล็อกอิน ใช้ geolocation + รัศมี 30 กม.)
    path('map/nearby/', views.nearby_map_view, name='map_nearby'),

    path('about/', views.about_view, name='about'),
    path('category/', views.category_view, name='category'),
]
