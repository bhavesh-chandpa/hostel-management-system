
from django import forms
from .models import Student, User


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




class RegistrationDecisionForm(forms.Form):

    DECISION_CHOICES = [
        ('approve', 'Approve Application'),
        ('reject', 'Reject Application'),
    ]

    decision = forms.ChoiceField(
        choices=DECISION_CHOICES,
        widget=forms.RadioSelect
    )

    username = forms.CharField(
        max_length=50,
        required=False,
        help_text='Username for the approved student account.'
    )

    temporary_password = forms.CharField(
        required=False,
        widget=forms.PasswordInput,
        help_text='Initial password for the student account.'
    )

    remarks = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text='Approval or rejection remarks.'
    )

    def clean(self):
        cleaned_data = super().clean()

        decision = cleaned_data.get('decision')
        username = cleaned_data.get('username')
        password = cleaned_data.get('temporary_password')

        if decision == 'approve':

            if not username:
                self.add_error(
                    'username',
                    'Username is required for approval.'
                )

            elif User.objects.filter(username=username).exists():
                self.add_error(
                    'username',
                    'This username is already taken.'
                )

            if not password:
                self.add_error(
                    'temporary_password',
                    'An initial password is required.'
                )

        return cleaned_data
