from django.db import models
# 1. Import User model ที่คุณสร้างขึ้นเอง
from users.models import User 

class Post(models.Model):
    
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'รออนุมัติ'
        APPROVED = 'APPROVED', 'อนุมัติแล้ว'
        REJECTED = 'REJECTED', 'ไม่อนุมัติ'
    # --- ข้อมูลหลักของกิจกรรม ---
    title = models.CharField(max_length=200, verbose_name="ชื่อกิจกรรม")
    description = models.TextField(verbose_name="รายละเอียดกิจกรรม")
    location = models.CharField(max_length=255, verbose_name="สถานที่")
    event_date = models.DateTimeField(blank=True,null=True,verbose_name="วันที่จัดกิจกรรม")
    slots_available = models.PositiveIntegerField(verbose_name="จำนวนที่รับสมัคร")
    image = models.ImageField(upload_to='activity_images/', null=True, blank=True, verbose_name="รูปภาพกิจกรรม")
    organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_posts")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="สถานะ"
    )

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})" # แสดง status ใน admin

    class Meta:
        ordering = ['-created_at']
