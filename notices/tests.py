from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from accounts.models import Staff, User
from .models import Notice

class NoticeWorkflowTests(TestCase):
    def setUp(self):
        self.staff = Staff.objects.create(
            full_name="Notice Rector", email="notice-rector@example.com",
            phone_number="9888888888", employee_number="NOTICE-RECTOR",
            joining_date=timezone.localdate(),
        )
        self.rector = User.objects.create_user(username="notice.rector", password="StrongPass@123", staff=self.staff, role=User.Role.RECTOR)
        self.notice = Notice.objects.create(title="Test notice", content="Notice body", posted_by=self.staff)

    def test_notice_is_visible_when_active(self):
        response = self.client.get(reverse("active_notices"))
        self.assertContains(response, "Test notice")

    def test_rector_can_deactivate_but_not_delete_notice(self):
        self.client.force_login(self.rector)
        response = self.client.post(reverse("deactivate_notice", args=[self.notice.pk]))
        self.assertRedirects(response, reverse("manage_notices"))
        self.notice.refresh_from_db()
        self.assertFalse(self.notice.is_active)
        self.assertTrue(Notice.objects.filter(pk=self.notice.pk).exists())
