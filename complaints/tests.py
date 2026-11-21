from django.test import TestCase
from django.urls import reverse
from accounts.models import Student, User
from .models import Complaint

class ComplaintWorkflowTests(TestCase):
    def setUp(self):
        self.student_profile = Student.objects.create(
            full_name="Complaint Student", email="complaint-student@example.com",
            phone_number="9666666666", date_of_birth="2005-01-01",
            roll_number="COMPLAINT-001", degree="BSc CS", year_of_study=3,
            guardian_contact="9777777777", home_address="Ahmedabad",
            student_status=Student.StudentStatus.ACTIVE,
        )
        self.student = User.objects.create_user(username="complaint.student", password="StrongPass@123", student=self.student_profile, role=User.Role.STUDENT)

    def test_student_can_submit_complaint(self):
        self.client.force_login(self.student)
        response = self.client.post(reverse("submit_complaint"), {
            "subject": "Water supply", "description": "Water supply is not working on the floor.",
        })
        self.assertRedirects(response, reverse("student_complaints"))
        self.assertTrue(Complaint.objects.filter(student=self.student_profile).exists())
