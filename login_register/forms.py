from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model

# ดึง Custom User Model ที่เราตั้งค่าไว้ใน settings.py (AUTH_USER_MODEL)
User = get_user_model()

class CustomUserCreationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        # ระบุ fields ที่จะแสดงในฟอร์มสมัครสมาชิก
        # เราใช้ email แทน username
        fields = ('email', 'first_name', 'last_name')