from django.contrib import admin
from .models import LeaveApplication


@admin.register(LeaveApplication)
class LeaveApplicationAdmin(admin.ModelAdmin):

    list_display = (
        'leave_id',
        'student',
        'reason',
        'from_date',
        'to_date',
        'status',
        'applied_at',
        'processed_by',
    )

    list_filter = (
        'status',
        'from_date',
        'applied_at',
    )

    search_fields = (
        'student__full_name',
        'student__roll_number',
        'reason',
    )

    readonly_fields = (
        'applied_at',
    )

    list_select_related = (
        'student',
        'processed_by',
    )

    ordering = (
        '-applied_at',
    )
