from django.test import TestCase
from django.utils import timezone
from .models import Staff, Student, User

class CustomUserModelTests(TestCase):
    def test_student_account_hashes_password(self):
        student = Student.objects.create(
            full_name="Test Student", email="test-student@example.com",
            phone_number="9000000001", date_of_birth="2005-01-01",
            roll_number="TEST-001", degree="BSc CS", year_of_study=3,
            guardian_contact="9000000002", home_address="Test Address",
            student_status=Student.StudentStatus.ACTIVE,
        )
        user = User.objects.create_user(
            username="test.student", password="StrongPass@123",
            student=student, role=User.Role.STUDENT,
        )
        self.assertNotEqual(user.password, "StrongPass@123")
        self.assertTrue(user.check_password("StrongPass@123"))
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)

    def test_rector_is_not_django_admin_staff(self):
        staff = Staff.objects.create(
            full_name="Test Rector", email="rector-test@example.com",
            phone_number="9000000003", employee_number="TEST-RECTOR",
            joining_date=timezone.localdate(),
        )
        user = User.objects.create_user(
            username="test.rector", password="StrongPass@123",
            staff=staff, role=User.Role.RECTOR,
        )
        self.assertFalse(user.is_staff)
        self.assertTrue(user.is_active)
