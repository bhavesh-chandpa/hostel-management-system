from django.core.management import call_command
from django.test import TestCase
from django.urls import reverse
from accounts.models import Student, User


class PublicRegistrationTests(TestCase):
    def test_homepage_loads(self):
        response = self.client.get(reverse("home"))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Your home away")

    def test_registration_creates_pending_application_without_login(self):
        response = self.client.post(reverse("register"), {
            "full_name": "Applicant Test", "email": "applicant@example.com",
            "phone_number": "9000000010", "date_of_birth": "2005-01-01",
            "roll_number": "APPLICANT-001", "degree": "BSc CS",
            "year_of_study": "3", "guardian_contact": "9000000011",
            "home_address": "Ahmedabad",
        })
        self.assertEqual(response.status_code, 200)
        student = Student.objects.get(email="applicant@example.com")
        self.assertEqual(student.student_status, Student.StudentStatus.PENDING)
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_demo_seed_command_is_repeatable(self):
        call_command("seed_demo")
        call_command("seed_demo")
        self.assertEqual(User.objects.filter(username="demo.rector").count(), 1)
        self.assertEqual(Student.objects.filter(roll_number="DEMO-PENDING-001").count(), 1)
