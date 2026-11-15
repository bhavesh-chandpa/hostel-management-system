from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm


class RegisterForm(UserCreationForm):

    email = forms.EmailField(required=True)

    class Meta(UserCreationForm.Meta):

        model = User

        fields = [
            'username',
            'email'
        ]


class LeaveApplicationForm(forms.Form):

    student_name = forms.CharField(
        max_length=100,
        label="Student Name"
    )

    room_number = forms.IntegerField(
        min_value=1,
        label="Room Number"
    )

    reason = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={
            'rows': 4,
            'placeholder': 'Enter reason for leave'
        })
    )

    start_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date'
        })
    )

    end_date = forms.DateField(
        widget=forms.DateInput(attrs={
            'type': 'date'
        })
    )