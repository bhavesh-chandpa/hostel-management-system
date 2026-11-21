
from django.contrib import admin
from .models import Complaint


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):

    list_display = (
        'complaint_id',
        'student',
        'subject',
        'status',
        'submitted_at',
        'resolved_by',
    )

    list_filter = (
        'status',
        'submitted_at',
    )

    search_fields = (
        'student__full_name',
        'student__roll_number',
        'subject',
        'description',
    )

    readonly_fields = (
        'submitted_at',
    )

    list_select_related = (
        'student',
        'resolved_by',
    )

    ordering = (
        '-submitted_at',
    )
