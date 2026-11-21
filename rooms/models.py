from django.db import models
from django.core.validators import MinValueValidator


class Room(models.Model):

    STATUS_CHOICES = [
        (True, 'Active'),
        (False, 'Under Maintenance'),
    ]

    # Primary key
    room_number = models.IntegerField(
        primary_key=True
    )

    # Maximum room occupancy
    capacity = models.SmallIntegerField(
        validators=[MinValueValidator(1)]
    )

    # True = Active, False = Under Maintenance
    status = models.BooleanField(
        choices=STATUS_CHOICES,
        default=True
    )

    class Meta:
        db_table = 'room_table'
        verbose_name = 'Room'
        verbose_name_plural = 'Rooms'

        constraints = [
            models.CheckConstraint(
                condition=models.Q(capacity__gte=1),
                name='room_capacity_positive'
            )
        ]

    def __str__(self):
        return f"Room {self.room_number}"



class RoomAllocation(models.Model):

    class RequestStatus(models.TextChoices):
        PENDING = 'Pending', 'Pending'
        APPROVED = 'Approved', 'Approved'
        REJECTED = 'Rejected', 'Rejected'

    # Primary key
    allocation_id = models.AutoField(
        primary_key=True
    )

    # Student receiving or requesting the room
    student = models.ForeignKey(
        'accounts.Student',
        on_delete=models.PROTECT,
        db_column='student_id',
        related_name='room_allocations'
    )

    # Allocated or requested room
    room_number = models.ForeignKey(
        Room,
        on_delete=models.PROTECT,
        to_field='room_number',
        db_column='room_number',
        related_name='allocations'
    )

    bed_number = models.CharField(max_length=10)

    # Rector or staff member deciding the allocation
    # NULL while a request is pending
    decided_by = models.ForeignKey(
        'accounts.Staff',
        on_delete=models.PROTECT,
        null=True,
        blank=True,
        db_column='decided_by',
        related_name='decided_allocations'
    )

    # NULL until the room is actually allocated
    allocated_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # Additional room-change request information
    request_reason = models.CharField(
        max_length=500,
        null=True,
        blank=True
    )

    request_status = models.CharField(
        max_length=10,
        choices=RequestStatus.choices,
        null=True,
        blank=True
    )

    request_submitted_at = models.DateTimeField(
        null=True,
        blank=True
    )

    reviewed_at = models.DateTimeField(
        null=True,
        blank=True
    )

    # Identifies the student's current allocation
    is_current = models.BooleanField(default=False)

    class Meta:
        db_table = 'room_allocation_table'
        verbose_name = 'Room Allocation'
        verbose_name_plural = 'Room Allocations'

    def __str__(self):
        return (
            f"{self.student.full_name} - "
            f"Room {self.room_number_id}"
        )