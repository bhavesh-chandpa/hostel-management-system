from django.db import models


class Attendance(models.Model):

    # Primary key
    attendance_id = models.AutoField(primary_key=True)

    # Student whose attendance is recorded
    student = models.ForeignKey(
        'accounts.Student',
        on_delete=models.PROTECT,
        db_column='student_id',
        related_name='attendance_records'
    )

    # Date of attendance
    attendance_date = models.DateField()

    # Convention: True = Present, False = Absent
    status = models.BooleanField(
        help_text='True = Present, False = Absent'
    )

    # Staff member who marked attendance
    marked_by = models.ForeignKey(
        'accounts.Staff',
        on_delete=models.PROTECT,
        db_column='marked_by',
        related_name='marked_attendance'
    )

    # Date and time when attendance was recorded
    marked_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'attendance_table'
        verbose_name = 'Attendance'
        verbose_name_plural = 'Attendance Records'

        # One attendance record per student per day
        constraints = [
            models.UniqueConstraint(
                fields=['student', 'attendance_date'],
                name='unique_student_attendance_per_day'
            )
        ]

    def __str__(self):
        return (
            f"{self.student.full_name} - "
            f"{self.attendance_date}"
        )
