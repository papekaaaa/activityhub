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
            'contact_info'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
        }