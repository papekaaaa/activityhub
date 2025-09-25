# Create your models here.
from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.translation import gettext_lazy as _

class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifiers
    for authentication instead of usernames.
    """
    def create_user(self, email, password, **extra_fields):
        """
        Create and save a User with the given email and password.
        """
        if not email:
            raise ValueError(_('The Email must be set'))
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        """
        Create and save a SuperUser with the given email and password.
        """
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError(_('Superuser must have is_staff=True.'))
        if extra_fields.get('is_superuser') is not True:
            raise ValueError(_('Superuser must have is_superuser=True.'))
        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    # --- 1. สร้าง Choices สำหรับ Role ---
    class Role(models.TextChoices):
        USER = 'USER', 'User'
        APPROVER = 'APPROVER', 'Approver'
        ADMIN = 'ADMIN', 'Admin'

    username = None
    email = models.EmailField(_('email address'), unique=True)
    
    # --- 2. เพิ่ม Field 'role' ---
    # โดยค่าเริ่มต้นของ user ใหม่ทุกคนจะเป็น 'USER'
    role = models.CharField(max_length=50, choices=Role.choices, default=Role.USER)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

class Profile(models.Model):
    # เชื่อม Profile กับ User แบบหนึ่งต่อหนึ่ง
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    
    # เพิ่ม fields ตามที่ออกแบบไว้ใน UI
    profile_picture = models.ImageField(upload_to='profile_pics/', null=True, blank=True, default='profile_pics/default.jpg')
    nickname = models.CharField(max_length=100, blank=True)
    birth_date = models.DateField(null=True, blank=True)
    phone_number = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    contact_info = models.CharField(max_length=255, blank=True, help_text="เช่น Line ID, Facebook")
    
    def __str__(self):
        return f'{self.user.email} Profile'

