from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from accounts.models import Staff, Student, User
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
        staff = Staff.objects.create(
            full_name="Complaint Rector", email="complaint-rector@example.com",
            phone_number="9777777771", employee_number="COMPLAINT-RECTOR",
            joining_date=timezone.localdate(),
        )
        self.rector = User.objects.create_user(username="complaint.rector", password="StrongPass@123", staff=staff, role=User.Role.RECTOR)
        self.rector_staff = staff

    def test_student_can_submit_complaint(self):
        self.client.force_login(self.student)
        response = self.client.post(reverse("submit_complaint"), {
            "subject": "Water supply", "description": "Water supply is not working on the floor.",
        })
        self.assertRedirects(response, reverse("student_complaints"))
        self.assertTrue(Complaint.objects.filter(student=self.student_profile).exists())

    def test_rector_can_respond_and_resolve_complaint(self):
        complaint = Complaint.objects.create(
            student=self.student_profile, subject="Water supply",
            description="Please check the water supply.",
        )
        self.client.force_login(self.rector)
        response = self.client.post(reverse("respond_complaint", args=[complaint.pk]), {
            "status": "Resolved", "response": "The maintenance issue has been fixed.",
        })
        self.assertRedirects(response, reverse("rector_complaints"))
        complaint.refresh_from_db()
        self.assertEqual(complaint.status, Complaint.ComplaintStatus.RESOLVED)
        self.assertEqual(complaint.resolved_by, self.rector_staff)
        self.assertTrue(complaint.response)
