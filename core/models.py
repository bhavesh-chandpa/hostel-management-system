from django.db import models


class Room(models.Model):

    room_number = models.CharField(max_length=10, unique=True)

    capacity = models.PositiveSmallIntegerField(default=2)

    is_available = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Room {self.room_number}" 