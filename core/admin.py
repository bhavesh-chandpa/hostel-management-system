from django.contrib import admin
from .models import Room


from django.contrib import admin
from .models import Room


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):

    list_display = (
        'id',
        'room_number',
        'capacity',
        'is_available',
        'created_at'
    )

    list_filter = (
        'is_available',
        'capacity'
    )

    search_fields = (
        'room_number',
    )

    ordering = (
        'room_number',
    )

    readonly_fields = (
        'created_at',
    )