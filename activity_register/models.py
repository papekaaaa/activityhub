from django.db import models
from django.conf import settings
from django.utils import timezone
from post.models import Post


class ActivityRegistration(models.Model):
    PREFIX_CHOICES = [
        ('นาย', 'นาย'),
        ('นางสาว', 'นางสาว'),
        ('นาง', 'นาง'),
    ]

    GENDER_CHOICES = [
        ('ชาย', 'ชาย'),
        ('หญิง', 'หญิง'),
        ('อื่นๆ', 'อื่นๆ'),
    ]

    YES_NO_CHOICES = [
        ('Y', 'Y'),
        ('N', 'N'),
    ]

    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "สมัครแล้ว"
        CANCEL_PENDING = "CANCEL_PENDING", "รอยืนยันยกเลิก"
        CANCELED = "CANCELED", "ยกเลิกแล้ว"

    class CancelReason(models.TextChoices):
        NOT_AVAILABLE = "NOT_AVAILABLE", "วันเวลานั้นไม่สะดวกแล้ว"
        HEALTH = "HEALTH", "มีปัญหาสุขภาพกระทันหัน"
        OTHER = "OTHER", "อื่นๆระบุ"

    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='registrations'
    )

    # ใครสมัคร
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='activity_registrations'
    )

    prefix = models.CharField(max_length=10, choices=PREFIX_CHOICES)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    birth_date = models.DateField()
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES)

    current_address = models.TextField()
    phone = models.CharField(max_length=20)
    email = models.EmailField()

    contact_channel = models.CharField(
        max_length=255,
        help_text="เช่น Facebook, IG, Line ID"
    )

    chronic_disease = models.CharField(max_length=255, blank=True)
    food_allergy = models.CharField(max_length=255, blank=True)
    drug_allergy = models.CharField(max_length=255, blank=True)

    field_ability = models.CharField(
        max_length=1,
        choices=YES_NO_CHOICES,
        help_text="ความสามารถในการเข้าร่วมกิจกรรมภาคสนาม"
    )

    consent_personal_data = models.BooleanField(
        help_text="ยินยอมให้ใช้ข้อมูลส่วนตัวเพื่อวัตถุประสงค์ในกิจกรรม"
    )
    consent_terms = models.BooleanField(
        help_text="ยอมรับเงื่อนไขและข้อกำหนดของกิจกรรม"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    # ✅ เพิ่ม: ระบบยกเลิก
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)
    cancel_reason = models.CharField(max_length=20, choices=CancelReason.choices, blank=True, default="")
    cancel_reason_other = models.CharField(max_length=255, blank=True, default="")
    canceled_at = models.DateTimeField(null=True, blank=True)

    cancel_undo_until = models.DateTimeField(null=True, blank=True)  # ✅ ย้อนกลับได้ 5 นาที
    cooldown_until = models.DateTimeField(null=True, blank=True)     # ✅ สมัครใหม่ได้อีกใน 1 ชม.

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["user", "post"], name="uniq_user_post_registration")
        ]

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.post.title}"

    def can_cancel(self) -> bool:
        if not self.post.event_date:
            return False
        # ยกเลิกได้ก่อนเริ่ม 1 วัน
        return timezone.now() <= (self.post.event_date - timezone.timedelta(days=1))

    def start_cancel_pending(self, reason: str, other: str = ""):
        now = timezone.now()
        self.status = self.Status.CANCEL_PENDING
        self.cancel_reason = reason
        self.cancel_reason_other = other or ""
        self.canceled_at = now
        self.cancel_undo_until = now + timezone.timedelta(minutes=5)
        self.save(update_fields=["status", "cancel_reason", "cancel_reason_other", "canceled_at", "cancel_undo_until"])

    def undo_cancel(self) -> bool:
        now = timezone.now()
        if self.status != self.Status.CANCEL_PENDING:
            return False
        if not self.cancel_undo_until or now > self.cancel_undo_until:
            return False

        self.status = self.Status.ACTIVE
        self.cancel_reason = ""
        self.cancel_reason_other = ""
        self.canceled_at = None
        self.cancel_undo_until = None
        self.save(update_fields=["status", "cancel_reason", "cancel_reason_other", "canceled_at", "cancel_undo_until"])
        return True

    def finalize_cancel_if_expired(self) -> bool:
        """
        พ้น 5 นาที -> ยกเลิกจริง (เปลี่ยนเป็น CANCELED) + ตั้ง cooldown 1 ชม.
        (ไม่ลบ record เพื่อเก็บ cooldown และประวัติ)
        """
        now = timezone.now()
        if self.status != self.Status.CANCEL_PENDING:
            return False
        if not self.cancel_undo_until or now <= self.cancel_undo_until:
            return False

        self.status = self.Status.CANCELED
        self.cooldown_until = now + timezone.timedelta(hours=1)
        self.save(update_fields=["status", "cooldown_until"])
        return True


class ActivityReview(models.Model):
    """
    รีวิวกิจกรรม 1 user ต่อ 1 post
    เงื่อนไขฝั่ง view จะบังคับว่า ต้องลงทะเบียน + กิจกรรมผ่านแล้ว
    """
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='activity_reviews'
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='activity_reviews'
    )

    rating = models.PositiveSmallIntegerField(default=0)   # 1–5
    comment = models.TextField(blank=True)

    image1 = models.ImageField(
        upload_to='review_images/',
        blank=True,
        null=True
    )
    image2 = models.ImageField(
        upload_to='review_images/',
        blank=True,
        null=True
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('post', 'user')
        ordering = ['-created_at']

    def __str__(self):
        return f"Review {self.post.title} by {self.user}"
