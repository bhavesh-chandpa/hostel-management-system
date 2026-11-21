from django import forms
from django.utils import timezone
from .models import LeaveApplication


class LeaveApplicationForm(forms.ModelForm):
    class Meta:
        model = LeaveApplication
        fields = ("reason", "from_date", "to_date")
        widgets = {
            "reason": forms.Textarea(attrs={"rows": 4, "class": "form-control", "placeholder": "Explain why you need leave"}),
            "from_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "to_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
        }

    def clean(self):
        cleaned = super().clean()
        start, end = cleaned.get("from_date"), cleaned.get("to_date")
        if start and end:
            if start < timezone.localdate():
                self.add_error("from_date", "Leave start date cannot be in the past.")
            if end < start:
                self.add_error("to_date", "End date must be on or after the start date.")
        return cleaned
