from django.db import models


class LeaveApplication(models.Model):

    class LeaveStatus(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        APPROVED = 'Approved', 'Approved'
        REJECTED = 'Rejected', 'Rejected'

    # Primary key
    leave_id = models.AutoField(primary_key=True)

    # Student who submitted the application
    student = models.ForeignKey(
        'accounts.Student',
        on_delete=models.PROTECT,
        db_column='student_id',
        related_name='leave_applications'
    )

    # Reason for requesting leave
    reason = models.CharField(max_length=250)

    # Leave duration
    from_date = models.DateField()
    to_date = models.DateField()

    # Current application status
    status = models.CharField(
        max_length=10,
        choices=LeaveStatus.choices,
        default=LeaveStatus.PENDING
    )

    # Application submission time
    applied_at = models.DateTimeField(auto_now_add=True)

    # Staff member who processed the application
    # NULL until a staff member processes it
    processed_by = models.ForeignKey(
        'accounts.Staff',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column='processed_by',
        related_name='processed_leave_applications'
    )

    class Meta:
        db_table = 'leave_table'
        verbose_name = 'Leave Application'
        verbose_name_plural = 'Leave Applications'

    def __str__(self):
        return (
            f"Leave #{self.leave_id} - "
            f"{self.student.full_name} - {self.status}"
        )
