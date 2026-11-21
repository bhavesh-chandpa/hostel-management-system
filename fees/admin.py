from django.contrib import admin
from .models import FeeStructure, Payment


@admin.register(FeeStructure)
class FeeStructureAdmin(admin.ModelAdmin):

    list_display = (
        'fee_structure_id',
        'amount',
        'effective_from',
        'updated_by',
    )

    list_filter = (
        'effective_from',
    )

    search_fields = (
        'updated_by__full_name',
    )

    list_select_related = (
        'updated_by',
    )

    ordering = (
        '-effective_from',
    )


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):

    list_display = (
        'payment_id',
        'student',
        'fee_structure',
        'due_date',
        'amount_paid',
        'payment_date',
        'receipt_number',
    )

    list_filter = (
        'due_date',
        'payment_date',
    )

    search_fields = (
        'student__full_name',
        'student__roll_number',
        'receipt_number',
    )

    list_select_related = (
        'student',
        'fee_structure',
    )

    ordering = (
        '-due_date',
    )