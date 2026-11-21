from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from accounts.models import Staff, Student, User
from .models import Room, RoomAllocation

class RoomWorkflowTests(TestCase):
    def setUp(self):
        today = timezone.localdate()
        staff = Staff.objects.create(
            full_name="Test Rector", email="rooms-rector@example.com",
            phone_number="9111111111", employee_number="ROOM-RECTOR", joining_date=today,
        )
        self.rector = User.objects.create_user(username="rooms.rector", password="StrongPass@123", staff=staff, role=User.Role.RECTOR)
        self.student_profile = Student.objects.create(
            full_name="Active Student", email="rooms-student@example.com",
            phone_number="9222222222", date_of_birth="2005-01-01",
            roll_number="ROOM-001", degree="BSc CS", year_of_study=3,
            guardian_contact="9333333333", home_address="Ahmedabad",
            student_status=Student.StudentStatus.ACTIVE,
        )
        self.student = User.objects.create_user(username="rooms.student", password="StrongPass@123", student=self.student_profile, role=User.Role.STUDENT)

    def test_rector_can_add_room_and_allocate_active_student(self):
        self.client.force_login(self.rector)
        response = self.client.post(reverse("room_management"), {
            "action": "add_room", "room-room_number": "101",
            "room-capacity": "1", "room-status": "True",
        })
        self.assertEqual(response.status_code, 302)
        room = Room.objects.get(pk=101)
        response = self.client.post(reverse("room_management"), {
            "action": "allocate_room", "allocation-student": str(self.student_profile.pk),
            "allocation-room_number": str(room.pk), "allocation-bed_number": "Bed 1",
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(RoomAllocation.objects.filter(student=self.student_profile, is_current=True).exists())

    def test_student_dashboard_shows_current_room(self):
        room = Room.objects.create(room_number=202, capacity=1, status=True)
        RoomAllocation.objects.create(student=self.student_profile, room_number=room, bed_number="Bed A", is_current=True, allocated_at=timezone.now())
        self.client.force_login(self.student)
        response = self.client.get(reverse("student_dashboard"))
        self.assertContains(response, "Room 202")
        self.assertContains(response, "Bed A")

    def test_student_cannot_access_rector_room_management(self):
        self.client.force_login(self.student)
        response = self.client.get(reverse("room_management"))
        self.assertEqual(response.status_code, 403)
