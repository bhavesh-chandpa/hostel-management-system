from django.contrib import admin
from .models import Attendance


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):

    list_display = (
        'attendance_id',
        'student',
        'attendance_date',
        'status',
        'marked_by',
        'marked_at',
    )

    list_filter = (
        'attendance_date',
        'status',
    )

    search_fields = (
        'student__full_name',
        'student__roll_number',
    )

    readonly_fields = (
        'marked_at',
    )

    list_select_related = (
        'student',
        'marked_by',
    )

    ordering = (
        '-attendance_date',
        'student',
    )
