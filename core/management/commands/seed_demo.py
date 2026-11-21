from datetime import date, timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from accounts.models import Staff, Student, User
from complaints.models import Complaint
from leave_management.models import LeaveApplication
from notices.models import Notice
from rooms.models import Room, RoomAllocation


class Command(BaseCommand):
    help = "Create repeatable local demo records for project demonstrations."

    def handle(self, *args, **options):
        today = timezone.localdate()
        rector, _ = Staff.objects.get_or_create(employee_number="DEMO-RECTOR", defaults={
            "full_name": "Demo Rector", "email": "rector@example.com",
            "phone_number": "9999990001", "joining_date": today, "employment_status": True,
        })
        assistant, _ = Staff.objects.get_or_create(employee_number="DEMO-ASSISTANT", defaults={
            "full_name": "Demo Assistant Rector", "email": "assistant@example.com",
            "phone_number": "9999990002", "joining_date": today, "employment_status": True,
        })
        student, _ = Student.objects.get_or_create(roll_number="DEMO-001", defaults={
            "full_name": "Demo Student", "email": "student@example.com",
            "phone_number": "9999990003", "date_of_birth": date(2005, 1, 1),
            "degree": "BSc CS", "year_of_study": 3, "guardian_contact": "9999990004",
            "home_address": "Demo Address, Ahmedabad",
            "student_status": Student.StudentStatus.ACTIVE, "hostel_admission_date": today,
        })
        # A pending application gives the Rector a record to review in demonstrations.
        Student.objects.get_or_create(roll_number="DEMO-PENDING-001", defaults={
            "full_name": "Demo Applicant", "email": "applicant@example.com",
            "phone_number": "9999990005", "date_of_birth": date(2006, 2, 2),
            "degree": "BSc CS", "year_of_study": 2, "guardian_contact": "9999990006",
            "home_address": "Demo Applicant Address, Ahmedabad",
            "student_status": Student.StudentStatus.PENDING,
        })

        demo_users = [
            ("demo.rector", "DemoRector@123", User.Role.RECTOR, {"staff": rector}),
            ("demo.assistant", "DemoAssistant@123", User.Role.ASSISTANT_RECTOR, {"staff": assistant}),
            ("demo.student", "DemoStudent@123", User.Role.STUDENT, {"student": student}),
        ]
        for username, password, role, profile in demo_users:
            if not User.objects.filter(username=username).exists():
                User.objects.create_user(
                    username=username, password=password, role=role,
                    account_status=User.AccountStatus.ACTIVE, **profile,
                )

        room, _ = Room.objects.get_or_create(room_number=101, defaults={"capacity": 2, "status": True})
        if not RoomAllocation.objects.filter(student=student, is_current=True).exists():
            if room.status and room.allocations.filter(is_current=True).count() < room.capacity:
                RoomAllocation.objects.create(
                    student=student, room_number=room, bed_number="Bed 1",
                    decided_by=rector, allocated_at=timezone.now(), is_current=True,
                )

        Notice.objects.get_or_create(title="Welcome to the hostel portal", defaults={
            "content": "Welcome. Please check this portal regularly for hostel announcements.",
            "posted_by": rector, "is_active": True,
        })
        LeaveApplication.objects.get_or_create(student=student, reason="Demo leave application", defaults={
            "from_date": today + timedelta(days=5), "to_date": today + timedelta(days=7),
            "status": LeaveApplication.LeaveStatus.PENDING,
        })
        Complaint.objects.get_or_create(student=student, subject="Demo maintenance request", defaults={
            "description": "This is sample content for demonstrating the complaint workflow.",
            "status": Complaint.ComplaintStatus.SUBMITTED,
        })

        self.stdout.write(self.style.SUCCESS("Demo data is ready."))
        self.stdout.write("Rector: demo.rector / DemoRector@123")
        self.stdout.write("Assistant Rector: demo.assistant / DemoAssistant@123")
        self.stdout.write("Student: demo.student / DemoStudent@123")
