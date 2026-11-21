from django import forms
from .models import Complaint

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ("subject", "description")
        widgets = {
            "subject": forms.TextInput(attrs={"class": "form-control", "placeholder": "Brief subject"}),
            "description": forms.Textarea(attrs={"rows": 5, "class": "form-control", "placeholder": "Describe your complaint"}),
        }

class ComplaintResponseForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ("status", "response")
        widgets = {
            "status": forms.Select(attrs={"class": "form-control"}),
            "response": forms.Textarea(attrs={"rows": 4, "class": "form-control", "placeholder": "Write a response for the student"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["status"].choices = [
            (Complaint.ComplaintStatus.IN_PROGRESS, "In Progress"),
            (Complaint.ComplaintStatus.RESOLVED, "Resolved"),
            (Complaint.ComplaintStatus.REJECTED, "Rejected"),
        ]

    def clean(self):
        cleaned = super().clean()
        status = cleaned.get("status")
        response = (cleaned.get("response") or "").strip()
        if status in (Complaint.ComplaintStatus.RESOLVED, Complaint.ComplaintStatus.REJECTED) and not response:
            self.add_error("response", "Please provide a response before closing this complaint.")
        cleaned["response"] = response
        return cleaned
