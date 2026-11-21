from django.contrib import admin
from .models import Notice


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):

    list_display = (
        'notice_id',
        'title',
        'posted_by',
        'posted_at',
        'is_active',
    )

    list_filter = (
        'is_active',
        'posted_at',
    )

    search_fields = (
        'title',
        'content',
        'posted_by__full_name',
    )

    readonly_fields = (
        'posted_at',
    )

    list_select_related = (
        'posted_by',
    )

    list_editable = (
        'is_active',
    )

    ordering = (
        '-posted_at',
    )

    # Notices must be deactivated, not permanently deleted.
    def has_delete_permission(self, request, obj=None):
        return False