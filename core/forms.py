from django import forms
from .models import Student


class StudentRegistrationForm(forms.ModelForm):

    class Meta:
        model = Student

        fields = [
            'full_name',
            'email',
            'phone_number',
            'date_of_birth',
            'roll_number',
            'degree',
            'year_of_study',
            'guardian_contact',
            'home_address',
        ]

        widgets = {
            'date_of_birth': forms.DateInput(
                attrs={'type': 'date'}
            ),

            'home_address': forms.Textarea(
                attrs={
                    'rows': 3,
                    'placeholder': 'Enter your permanent address'
                }
            ),

            'year_of_study': forms.NumberInput(
                attrs={'min': 1}
            ),
        }

    def clean_email(self):
        email = self.cleaned_data['email']
        return email.lower()
