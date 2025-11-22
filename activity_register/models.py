from django.db import models
from django.conf import settings
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

    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.post.title}"


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
