# # from django.db import models
# # # 1. Import User model ที่คุณสร้างขึ้นเอง
# # from users.models import User 

# # class Post(models.Model):
    
# #     class Status(models.TextChoices):
# #         PENDING = 'PENDING', 'รออนุมัติ'
# #         APPROVED = 'APPROVED', 'อนุมัติแล้ว'
# #         REJECTED = 'REJECTED', 'ไม่อนุมัติ'
# #     # --- ข้อมูลหลักของกิจกรรม ---
# #     title = models.CharField(max_length=200, verbose_name="ชื่อกิจกรรม")
# #     description = models.TextField(verbose_name="รายละเอียดกิจกรรม")
# #     location = models.CharField(max_length=255, verbose_name="สถานที่")
# #     event_date = models.DateTimeField(blank=True,null=True,verbose_name="วันที่จัดกิจกรรม")
# #     slots_available = models.PositiveIntegerField(verbose_name="จำนวนที่รับสมัคร")
# #     image = models.ImageField(upload_to='activity_images/', null=True, blank=True, verbose_name="รูปภาพกิจกรรม")
# #     organizer = models.ForeignKey(User, on_delete=models.CASCADE, related_name="organized_posts")
# #     created_at = models.DateTimeField(auto_now_add=True)
# #     updated_at = models.DateTimeField(auto_now=True)

# #     status = models.CharField(
# #         max_length=10,
# #         choices=Status.choices,
# #         default=Status.PENDING,
# #         verbose_name="สถานะ"
# #     )

# #     def __str__(self):
# #         return f"{self.title} ({self.get_status_display()})" # แสดง status ใน admin

# #     class Meta:
# #         ordering = ['-created_at']

# from django.db import models
# from django.conf import settings

# class Post(models.Model):
#     CATEGORY_CHOICES = [
#         ("จิตอาสาด้านสาธารณประโยชน์", "จิตอาสาด้านสาธารณประโยชน์"),
#         ("จิตอาสาด้านการศึกษา", "จิตอาสาด้านการศึกษา"),
#         ("จิตอาสาด้านสุขภาพ", "จิตอาสาด้านสุขภาพ"),
#         ("จิตอาสาด้านสิ่งแวดล้อม", "จิตอาสาด้านสิ่งแวดล้อม"),
#         ("จิตอาสาด้านภัยพิบัติและบรรเทาทุกข์", "จิตอาสาด้านภัยพิบัติและบรรเทาทุกข์"),
#         ("จิตอาสาด้านศาสนาและวัฒนธรรม", "จิตอาสาด้านศาสนาและวัฒนธรรม"),
#         ("จิตอาสาด้านเทคโนโลยีและสื่อสาร", "จิตอาสาด้านเทคโนโลยีและสื่อสาร"),
#         ("จิตอาสาด้านเยาวชนและเด็ก", "จิตอาสาด้านเยาวชนและเด็ก"),
#         ("จิตอาสาด้านสัตว์และสิ่งมีชีวิต", "จิตอาสาด้านสัตว์และสิ่งมีชีวิต"),
#         ("กิจกรรมรณรงค์/ประกวด", "กิจกรรมรณรงค์/ประกวด"),
#     ]

#     title = models.CharField(max_length=200, verbose_name="ชื่อกิจกรรม")
#     location = models.CharField(max_length=200, verbose_name="สถานที่")
#     date = models.DateField(verbose_name="วันที่จัดกิจกรรม")
#     description = models.TextField(verbose_name="รายละเอียด")
#     image = models.ImageField(upload_to='posts/', blank=True, null=True, verbose_name="รูปกิจกรรม")
#     schedule = models.FileField(upload_to='schedules/', blank=True, null=True, verbose_name="กำหนดการ (ไฟล์)")
#     map_lat = models.FloatField(blank=True, null=True, verbose_name="ละติจูด")
#     map_lng = models.FloatField(blank=True, null=True, verbose_name="ลองจิจูด")
#     capacity = models.PositiveIntegerField(default=1, verbose_name="จำนวนคนที่รับสมัคร")
#     category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, verbose_name="ประเภทกิจกรรม")
#     created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="ผู้สร้างโพสต์")
#     created_at = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return self.title

# post/models.py
from django.db import models
from django.conf import settings  # ✅ รองรับ CustomUser

class Post(models.Model):

    CATEGORY_CHOICES = [
        ("จิตอาสาด้านสาธารณประโยชน์", "จิตอาสาด้านสาธารณประโยชน์"),
        ("จิตอาสาด้านการศึกษา", "จิตอาสาด้านการศึกษา"),
        ("จิตอาสาด้านสุขภาพ", "จิตอาสาด้านสุขภาพ"),
        ("จิตอาสาด้านสิ่งแวดล้อม", "จิตอาสาด้านสิ่งแวดล้อม"),
        ("จิตอาสาด้านภัยพิบัติและบรรเทาทุกข์", "จิตอาสาด้านภัยพิบัติและบรรเทาทุกข์"),
        ("จิตอาสาด้านศาสนาและวัฒนธรรม", "จิตอาสาด้านศาสนาและวัฒนธรรม"),
        ("จิตอาสาด้านเทคโนโลยีและสื่อสาร", "จิตอาสาด้านเทคโนโลยีและสื่อสาร"),
        ("จิตอาสาด้านเยาวชนและเด็ก", "จิตอาสาด้านเยาวชนและเด็ก"),
        ("จิตอาสาด้านสัตว์และสิ่งมีชีวิต", "จิตอาสาด้านสัตว์และสิ่งมีชีวิต"),
        ("กิจกรรมรณรงค์/ประกวด", "กิจกรรมรณรงค์/ประกวด"),
    ]

    class Status(models.TextChoices):
        PENDING = 'PENDING', 'รออนุมัติ'
        APPROVED = 'APPROVED', 'อนุมัติแล้ว'
        REJECTED = 'REJECTED', 'ไม่อนุมัติ'

    title = models.CharField(max_length=200, verbose_name="ชื่อกิจกรรม")
    description = models.TextField(verbose_name="รายละเอียดกิจกรรม")
    location = models.CharField(max_length=255, verbose_name="สถานที่")
    event_date = models.DateTimeField(blank=True, null=True, verbose_name="วันที่จัดกิจกรรม")
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES, verbose_name="ประเภทกิจกรรม")

    # ✅ จำนวนที่รับสมัคร
    slots_available = models.PositiveIntegerField(verbose_name="จำนวนที่รับสมัคร")

    # ✅ ค่าใช้จ่าย (ไม่กรอก = ไม่มีค่าใช้จ่าย)
    fee = models.PositiveIntegerField(
        blank=True,
        null=True,
        verbose_name="ค่าใช้จ่าย (บาท)"
    )

    # ✅ เปิด / ปิด ให้สมัครผ่านระบบ (ควบคุมปุ่ม “สมัคร” หน้า home)
    allow_register = models.BooleanField(
        default=True,
        verbose_name="เปิดให้ลงทะเบียนผ่านระบบ"
    )

    # ✅ ไฟล์รูป / เอกสารกำหนดการ
    image = models.ImageField(upload_to='activity_images/', null=True, blank=True, verbose_name="รูปภาพกิจกรรม")
    schedule = models.FileField(upload_to='schedules/', null=True, blank=True, verbose_name="กำหนดการ (ไฟล์)")

    # ✅ พิกัดแผนที่
    map_lat = models.FloatField(blank=True, null=True, verbose_name="ละติจูด")
    map_lng = models.FloatField(blank=True, null=True, verbose_name="ลองจิจูด")

    # ✅ เลือกว่าจะสร้างกลุ่มแชตให้กิจกรรมนี้หรือไม่ (ใช้ต่อในอนาคต)
    create_group = models.BooleanField(
        default=False,
        verbose_name="สร้างกลุ่มสำหรับกิจกรรมนี้"
    )

    organizer = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="organized_posts",
        verbose_name="ผู้สร้างโพสต์"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="สร้างเมื่อ")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="แก้ไขล่าสุด")

    # ✅ ระบบถูกใจและจัดเก็บ
    likes = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='liked_posts', blank=True
    )
    saves = models.ManyToManyField(
        settings.AUTH_USER_MODEL, related_name='saved_posts', blank=True
    )

    status = models.CharField(
        max_length=10,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="สถานะ"
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = "โพสต์กิจกรรม"
        verbose_name_plural = "โพสต์กิจกรรมทั้งหมด"

    def __str__(self):
        return f"{self.title} ({self.get_status_display()})"
