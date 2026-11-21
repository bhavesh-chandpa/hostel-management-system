from datetime import timedelta
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from accounts.models import Staff, Student, User
from .models import LeaveApplication

class LeaveWorkflowTests(TestCase):
    def setUp(self):
        self.today = timezone.localdate()
        self.student_profile = Student.objects.create(
            full_name="Leave Student", email="leave-student@example.com",
            phone_number="9444444444", date_of_birth="2005-01-01",
            roll_number="LEAVE-001", degree="BSc CS", year_of_study=3,
            guardian_contact="9555555555", home_address="Ahmedabad",
            student_status=Student.StudentStatus.ACTIVE,
        )
        self.student = User.objects.create_user(username="leave.student", password="StrongPass@123", student=self.student_profile, role=User.Role.STUDENT)
        staff = Staff.objects.create(
            full_name="Leave Rector", email="leave-rector@example.com",
            phone_number="9666666661", employee_number="LEAVE-RECTOR",
            joining_date=self.today,
        )
        self.rector = User.objects.create_user(username="leave.rector", password="StrongPass@123", staff=staff, role=User.Role.RECTOR)
        self.rector_staff = staff

    def test_student_can_submit_leave(self):
        self.client.force_login(self.student)
        response = self.client.post(reverse("apply_leave"), {
            "reason": "Family visit", "from_date": (self.today + timedelta(days=2)).isoformat(),
            "to_date": (self.today + timedelta(days=3)).isoformat(),
        })
        self.assertRedirects(response, reverse("student_leave_list"))
        leave = LeaveApplication.objects.get(student=self.student_profile)
        self.assertEqual(leave.status, LeaveApplication.LeaveStatus.PENDING)

    def test_end_date_before_start_date_is_rejected(self):
        self.client.force_login(self.student)
        response = self.client.post(reverse("apply_leave"), {
            "reason": "Invalid dates", "from_date": (self.today + timedelta(days=5)).isoformat(),
            "to_date": (self.today + timedelta(days=2)).isoformat(),
        })
        self.assertEqual(response.status_code, 200)
        self.assertFalse(LeaveApplication.objects.exists())

    def test_rector_can_approve_pending_leave(self):
        leave = LeaveApplication.objects.create(
            student=self.student_profile, reason="Family visit",
            from_date=self.today + timedelta(days=2),
            to_date=self.today + timedelta(days=3),
        )
        self.client.force_login(self.rector)
        response = self.client.post(reverse("decide_leave", args=[leave.pk]), {"decision": "Approved"})
        self.assertRedirects(response, reverse("rector_leave_list"))
        leave.refresh_from_db()
        self.assertEqual(leave.status, LeaveApplication.LeaveStatus.APPROVED)
        self.assertEqual(leave.processed_by, self.rector_staff)
