from django.urls import path
from . import views

app_name = "activity_register"

urlpatterns = [
    path("register/<int:post_id>/", views.register_activity, name="register_activity"),
    path("cancel/<int:post_id>/", views.cancel_activity, name="cancel_activity"),
    path("cancel/<int:post_id>/undo/", views.undo_cancel_activity, name="undo_cancel_activity"),
    path("finalize/<int:post_id>/", views.finalize_cancel_ajax, name="finalize_cancel_ajax"),

    path("profile/edit/", views.edit_register_profile, name="edit_register_profile"),
    path("joined/", views.joined_activities, name="joined_activities"),
    path("review/<int:post_id>/", views.review_activity, name="review_activity"),
]
