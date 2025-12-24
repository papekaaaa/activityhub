from django.urls import path
from . import views

app_name = "notifications"

urlpatterns = [
    path("api/list/", views.api_list_notifications, name="api_list"),
    path("api/read/<int:notif_id>/", views.api_mark_read, name="api_mark_read"),
]
