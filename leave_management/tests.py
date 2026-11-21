from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from accounts.models import Student, User
from .models import LeaveApplication

class LeaveWorkflowTests(TestCase):
    def setUp(self):
        self.student_profile = Student.objects.create(
            full_name="Leave Student", email="leave-student@example.com",
            phone_number="9444444444", date_of_birth="2005-01-01",
            roll_number="LEAVE-001", degree="BSc CS", year_of_study=3,
            guardian_contact="9555555555", home_address="Ahmedabad",
            student_status=Student.StudentStatus.ACTIVE,
        )
        self.student = User.objects.create_user(username="leave.student", password="StrongPass@123", student=self.student_profile, role=User.Role.STUDENT)

    def test_student_can_submit_leave(self):
        today = timezone.localdate()
        self.client.force_login(self.student)
        response = self.client.post(reverse("apply_leave"), {
            "reason": "Family visit", "from_date": (today + timedelta(days=2)).isoformat(),
            "to_date": (today + timedelta(days=3)).isoformat(),
        })
        self.assertRedirects(response, reverse("student_leave_list"))
        leave = LeaveApplication.objects.get(student=self.student_profile)
        self.assertEqual(leave.status, LeaveApplication.LeaveStatus.PENDING)

    def test_end_date_before_start_date_is_rejected(self):
        today = timezone.localdate()
        self.client.force_login(self.student)
        response = self.client.post(reverse("apply_leave"), {
            "reason": "Invalid dates", "from_date": (today + timedelta(days=5)).isoformat(),
            "to_date": (today + timedelta(days=2)).isoformat(),
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(LeaveApplication.objects.exists())
