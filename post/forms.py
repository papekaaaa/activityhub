# # post/forms.py

# from django import forms
# from .models import Post

# class PostForm(forms.ModelForm):
#     # กำหนด widget ให้ event_date แสดงผลเป็นช่องให้เลือกวันที่และเวลาได้ง่าย
#     event_date = forms.DateTimeField(
#         widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}),
#     )

#     class Meta:
#         model = Post
#         # เลือกฟิลด์ที่ต้องการให้ผู้ใช้กรอกในฟอร์ม
#         fields = [
#             'title', 
#             'description', 
#             'location', 
#             'event_date', 
#             'slots_available', 
#             'image'
#         ]

# from django import forms
# from .models import Post

# class PostForm(forms.ModelForm):
#     class Meta:
#         model = Post
#         fields = [
#             'title', 'location', 'date', 'description', 
#             'image', 'schedule', 'map_lat', 'map_lng', 
#             'capacity', 'category'
#         ]
#         widgets = {
#             'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
#             'description': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
#         }

from django import forms
from .models import Post

class PostForm(forms.ModelForm):
    # ใช้ widget ที่ให้เลือก "วันที่และเวลา" สำหรับฟิลด์ event_date
    event_date = forms.DateTimeField(
        widget=forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        }),
        label="วันที่จัดกิจกรรม"
    )

    class Meta:
        model = Post
        fields = [
            'title', 
            'description', 
            'location', 
            'event_date', 
            'slots_available',
            'image', 
            'schedule', 
            'map_lat', 
            'map_lng',
            'category'
        ]

        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ชื่อกิจกรรม'
            }),
            'description': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'รายละเอียดกิจกรรม'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'สถานที่จัดกิจกรรม'
            }),
            'slots_available': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': 1
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'schedule': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'map_lat': forms.HiddenInput(),
            'map_lng': forms.HiddenInput(),
            'category': forms.Select(attrs={
                'class': 'form-select'
            }),
        }
