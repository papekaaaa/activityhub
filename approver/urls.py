from django.urls import path
from . import views

urlpatterns = [
    path("", views.approver_dashboard, name="approver_dashboard"),
    path("post/<int:post_id>/approve/", views.approve_post, name="approve_post"),
    path("post/<int:post_id>/reject/", views.reject_post, name="reject_post"),

    # ✅ ซ่อน / ลบโพสต์แบบ soft delete
    path("post/<int:post_id>/hide/", views.hide_post, name="hide_post"),
    path("post/<int:post_id>/soft-delete/", views.soft_delete_post, name="soft_delete_post"),

    # ✅ ปิดการใช้งานบัญชี (โปรไฟล์)
    path("user/<int:user_id>/deactivate/", views.deactivate_user, name="deactivate_user"),
    path("post/<int:post_id>/restore/", views.restore_post, name="restore_post"),

    # ✅ รายงาน (ผู้ใช้ทั่วไป)
    path("report/post/<int:post_id>/submit/", views.submit_post_report, name="submit_post_report"),
    path("report/user/<int:user_id>/submit/", views.submit_user_report, name="submit_user_report"),

    # ✅ จัดการรายงาน (Approver/Admin)
    path("report/post/<int:report_id>/hide/", views.handle_post_report_hide, name="handle_post_report_hide"),
    path("report/post/<int:report_id>/delete/", views.handle_post_report_delete, name="handle_post_report_delete"),
    path("report/user/<int:report_id>/reject/", views.handle_user_report_reject, name="handle_user_report_reject"),
    path("report/user/<int:report_id>/deactivate/", views.handle_user_report_deactivate, name="handle_user_report_deactivate"),
]
