from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path("inbox/", views.inbox_view, name="inbox"),
    path("activity/<int:post_id>/", views.activity_chat_view, name="activity_chat"),
    path("dm/<str:email>/", views.dm_chat_view, name="dm_chat"),

    # ✅ อัปโหลดรูป/ไฟล์
    path("upload/<int:room_id>/", views.upload_message_view, name="upload_message"),

    # ✅ ลบห้องแชท (ของตัวเอง)
    path("delete/<int:room_id>/", views.delete_chat_room_view, name="delete_chat_room"),
]
