from django.urls import path
from .views import *

urlpatterns = [
    # ... url อื่นๆ
    path('', login_view, name='login'),
    path('register/', register_view, name='register'),
    path('logout/', logout_view, name='logout'),

    # ✅ เพิ่ม 2 หน้า: ข้อตกลง/Privacy
    path('terms/', terms_view, name='terms'),
    path('privacy/', privacy_view, name='privacy'),
    # ...
]
