# approver/models.py
from django.db import models
from django.conf import settings

from post.models import Post


class PostReport(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "รอดำเนินการ"
        RESOLVED = "RESOLVED", "จัดการแล้ว"
        REJECTED = "REJECTED", "ไม่เข้าข่าย"

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="post_reports_made",
        verbose_name="ผู้รายงาน"
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name="post_reports",
        verbose_name="โพสต์ที่ถูกรายงาน"
    )

    reason = models.TextField(verbose_name="เหตุผล")
    evidence_image = models.ImageField(
        upload_to="report_evidence/posts/",
        null=True,
        blank=True,
        verbose_name="รูปหลักฐาน (ถ้ามี)"
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="สถานะ"
    )

    handled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="post_reports_handled",
        verbose_name="ผู้จัดการรายงาน"
    )
    handled_at = models.DateTimeField(null=True, blank=True, verbose_name="จัดการเมื่อ")
    action_note = models.CharField(max_length=255, blank=True, default="", verbose_name="ผลการจัดการ")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="รายงานเมื่อ")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "รายงานโพสต์"
        verbose_name_plural = "รายงานโพสต์"

    def __str__(self):
        return f"PostReport#{self.id} post={self.post_id} by={self.reporter_id} ({self.status})"


class UserReport(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "รอดำเนินการ"
        RESOLVED = "RESOLVED", "จัดการแล้ว"
        REJECTED = "REJECTED", "ไม่เข้าข่าย"

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_reports_made",
        verbose_name="ผู้รายงาน"
    )

    # ใช้ชื่อ field ว่า user เพื่อให้เข้ากับ dashboard.html ปัจจุบัน (r.user)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="user_reports_received",
        verbose_name="บัญชีที่ถูกรายงาน"
    )

    reason = models.TextField(verbose_name="เหตุผล")
    evidence_image = models.ImageField(
        upload_to="report_evidence/users/",
        null=True,
        blank=True,
        verbose_name="รูปหลักฐาน (ถ้ามี)"
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="สถานะ"
    )

    handled_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="user_reports_handled",
        verbose_name="ผู้จัดการรายงาน"
    )
    handled_at = models.DateTimeField(null=True, blank=True, verbose_name="จัดการเมื่อ")
    action_note = models.CharField(max_length=255, blank=True, default="", verbose_name="ผลการจัดการ")

    created_at = models.DateTimeField(auto_now_add=True, verbose_name="รายงานเมื่อ")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "รายงานบัญชี"
        verbose_name_plural = "รายงานบัญชี"

    def __str__(self):
        return f"UserReport#{self.id} user={self.user_id} by={self.reporter_id} ({self.status})"
