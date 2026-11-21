from django.db import models


class Complaint(models.Model):

    class ComplaintStatus(models.TextChoices):
        SUBMITTED = 'Submitted', 'Submitted'
        IN_PROGRESS = 'In Progress', 'In Progress'
        RESOLVED = 'Resolved', 'Resolved'
        REJECTED = 'Rejected', 'Rejected'

    # Primary key
    complaint_id = models.AutoField(primary_key=True)

    # Student who submitted the complaint
    student = models.ForeignKey(
        'accounts.Student',
        on_delete=models.PROTECT,
        db_column='student_id',
        related_name='complaints'
    )

    # Complaint details
    subject = models.CharField(max_length=50)
    description = models.TextField()

    # Current complaint status
    status = models.CharField(
        max_length=20,
        choices=ComplaintStatus.choices,
        default=ComplaintStatus.SUBMITTED
    )

    # Automatically records submission time
    submitted_at = models.DateTimeField(auto_now_add=True)

    # Staff member who responds to the complaint
    resolved_by = models.ForeignKey(
        'accounts.Staff',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column='resolved_by',
        related_name='handled_complaints'
    )

    # Staff response
    response = models.TextField(
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'complaint_table'
        verbose_name = 'Complaint'
        verbose_name_plural = 'Complaints'

    def __str__(self):
        return (
            f"Complaint #{self.complaint_id} - "
            f"{self.subject}"
        )
