# post/forms.py

from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    # กำหนด widget ให้ event_date แสดงผลเป็นช่องให้เลือกวันที่และเวลาได้ง่าย
    event_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
    )

    class Meta:
        model = Post
        # เลือกฟิลด์ที่ต้องการให้ผู้ใช้กรอกในฟอร์ม
        fields = [
            'title', 
            'description', 
            'location', 
            'event_date', 
            'slots_available', 
            'image'
        ]