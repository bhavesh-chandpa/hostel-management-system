from django.contrib import admin
from .forms import RoomForm
from .models import Room, RoomAllocation


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    form = RoomForm
    list_display = ("room_number", "capacity", "status")
    list_filter = ("status", "capacity")
    search_fields = ("=room_number",)
    ordering = ("room_number",)


@admin.register(RoomAllocation)
class RoomAllocationAdmin(admin.ModelAdmin):
    list_display = (
        "allocation_id", "student", "room_number", "bed_number",
        "decided_by", "request_status", "is_current", "allocated_at",
    )
    list_filter = ("request_status", "is_current")
    search_fields = ("student__full_name", "bed_number")
    list_select_related = ("student", "room_number", "decided_by")
    list_display_links = None
    readonly_fields = (
        "allocation_id", "student", "room_number", "bed_number", "decided_by",
        "allocated_at", "request_reason", "request_status",
        "request_submitted_at", "reviewed_at", "is_current",
    )

    def has_add_permission(self, request):
        return False

    def has_change_permission(self, request, obj=None):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
