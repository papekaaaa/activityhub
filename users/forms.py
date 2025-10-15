# users/forms.py

from django import forms
from .models import User, Profile

class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = [
            'profile_picture',
            'nickname',
            'birth_date',
            'phone_number',
            'address',
            'gender',
            'phone',
            'contact_info'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'gender': forms.Select(choices=[('ชาย', 'ชาย'), ('หญิง', 'หญิง'), ('อื่นๆ', 'อื่นๆ')]),
        }

from django import forms
from .models import Profile
from django.contrib.auth.models import User




