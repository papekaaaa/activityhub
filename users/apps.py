from django.apps import AppConfig

class UsersConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'users'
    
    def ready(self):
        # 2. ย้าย import มาไว้ในนี้ที่เดียว และแก้ไขชื่อไฟล์ให้ถูกต้อง
        # จาก users.signal เป็น users.signals (เติม s)
        import users.signals