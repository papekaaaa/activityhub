from django import forms
from .models import ActivityRegistration, ActivityReview


class ActivityRegistrationForm(forms.ModelForm):
    class Meta:
        model = ActivityRegistration
        fields = [
            'prefix', 'first_name', 'last_name',
            'birth_date', 'gender',
            'current_address', 'phone', 'email',
            'contact_channel',
            'chronic_disease', 'food_allergy', 'drug_allergy',
            'field_ability',
            'consent_personal_data', 'consent_terms',
        ]
        widgets = {
            'prefix': forms.Select(attrs={'class': 'form-select'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'birth_date': forms.DateInput(
                attrs={'class': 'form-control', 'type': 'date'}
            ),
            'gender': forms.Select(attrs={'class': 'form-select'}),
            'current_address': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 2}
            ),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'contact_channel': forms.TextInput(attrs={'class': 'form-control'}),
            'chronic_disease': forms.TextInput(attrs={'class': 'form-control'}),
            'food_allergy': forms.TextInput(attrs={'class': 'form-control'}),
            'drug_allergy': forms.TextInput(attrs={'class': 'form-control'}),
            'field_ability': forms.Select(attrs={'class': 'form-select'}),
            'consent_personal_data': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'consent_terms': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

        error_messages = {
            'prefix': {'required': 'โปรดเลือกคำนำหน้า'},
            'first_name': {'required': 'กรุณากรอกชื่อ'},
            'last_name': {'required': 'กรุณากรอกนามสกุล'},
            'birth_date': {'required': 'กรุณากรอกวัน/เดือน/ปีเกิด'},
            'gender': {'required': 'กรุณาเลือกเพศ'},
            'current_address': {'required': 'กรุณากรอกที่อยู่ปัจจุบัน'},
            'phone': {'required': 'กรุณากรอกเบอร์โทรศัพท์'},
            'email': {'required': 'กรุณากรอกอีเมล'},
            'contact_channel': {'required': 'กรุณากรอกช่องทางการติดต่อ'},
            'field_ability': {'required': 'กรุณาเลือกความสามารถในการเข้าร่วมภาคสนาม'},
        }

    def clean(self):
        cleaned_data = super().clean()
        consent1 = cleaned_data.get('consent_personal_data')
        consent2 = cleaned_data.get('consent_terms')

        if not consent1:
            self.add_error(
                'consent_personal_data',
                'คุณต้องยินยอมให้ใช้ข้อมูลส่วนตัวก่อนจึงจะสมัครได้'
            )

        if not consent2:
            self.add_error(
                'consent_terms',
                'คุณต้องยอมรับเงื่อนไขและข้อกำหนดของกิจกรรม'
            )

        return cleaned_data


class ActivityReviewForm(forms.ModelForm):
    class Meta:
        model = ActivityReview
        fields = ['rating', 'comment', 'image1', 'image2']
        widgets = {
            'rating': forms.HiddenInput(),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'เล่าประสบการณ์/ความรู้สึกของคุณเกี่ยวกับกิจกรรมนี้',
            }),
            'image1': forms.ClearableFileInput(attrs={'class': 'form-control'}),
            'image2': forms.ClearableFileInput(attrs={'class': 'form-control'}),
        }
