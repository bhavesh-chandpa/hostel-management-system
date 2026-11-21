from django.contrib import admin
from .models import Room, RoomAllocation


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):

    list_display = (
        'room_number',
        'capacity',
        'status',
    )

    list_filter = (
        'status',
        'capacity',
    )

    search_fields = (
        '=room_number',
    )

    ordering = (
        'room_number',
    )


@admin.register(RoomAllocation)
class RoomAllocationAdmin(admin.ModelAdmin):

    list_display = (
        'allocation_id',
        'student',
        'room_number',
        'bed_number',
        'decided_by',
        'request_status',
        'is_current',
        'allocated_at',
    )

    list_filter = (
        'request_status',
        'is_current',
    )

    search_fields = (
        'student__full_name',
        'bed_number',
    )

    readonly_fields = (
        'allocated_at',
        'request_submitted_at',
        'reviewed_at',
    )

    list_select_related = (
        'student',
        'room_number',
        'decided_by',
    )
