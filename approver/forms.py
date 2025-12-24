# approver/forms.py
from django import forms
from .models import PostReport, UserReport


class PostReportForm(forms.ModelForm):
    class Meta:
        model = PostReport
        fields = ["reason", "evidence_image"]

    def clean_reason(self):
        reason = (self.cleaned_data.get("reason") or "").strip()
        if not reason:
            raise forms.ValidationError("กรุณากรอกเหตุผลในการรายงาน")
        return reason


class UserReportForm(forms.ModelForm):
    class Meta:
        model = UserReport
        fields = ["reason", "evidence_image"]

    def clean_reason(self):
        reason = (self.cleaned_data.get("reason") or "").strip()
        if not reason:
            raise forms.ValidationError("กรุณากรอกเหตุผลในการรายงาน")
        return reason
