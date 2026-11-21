from django import forms
from .models import Notice


class NoticeForm(forms.ModelForm):
    class Meta:
        model = Notice
        fields = ("title", "content")
        widgets = {
            "title": forms.TextInput(attrs={"class": "form-control", "placeholder": "Notice title"}),
            "content": forms.Textarea(attrs={"rows": 5, "class": "form-control", "placeholder": "Write the notice"}),
        }
