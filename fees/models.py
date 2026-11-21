from django.db import models


class FeeStructure(models.Model):

    # Primary key
    fee_structure_id = models.AutoField(primary_key=True)

    # Hostel fee amount
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2
    )

    # Date from which this fee becomes effective
    effective_from = models.DateField()

    # Staff member who updated the fee structure
    updated_by = models.ForeignKey(
        'accounts.Staff',
        on_delete=models.PROTECT,
        db_column='updated_by',
        related_name='updated_fee_structures'
    )

    class Meta:
        db_table = 'fee_structure_table'
        verbose_name = 'Fee Structure'
        verbose_name_plural = 'Fee Structures'

    def __str__(self):
        return f"Fee Structure #{self.fee_structure_id} - ₹{self.amount}"


class Payment(models.Model):

    # Primary key
    payment_id = models.AutoField(primary_key=True)

    # Student associated with this payment
    student = models.ForeignKey(
        'accounts.Student',
        on_delete=models.PROTECT,
        db_column='student_id',
        related_name='payments'
    )

    # Fee structure used to calculate the payment
    fee_structure = models.ForeignKey(
        FeeStructure,
        on_delete=models.PROTECT,
        db_column='fee_structure_id',
        related_name='payments'
    )

    # Payment due date
    due_date = models.DateField()

    # Amount paid by the student
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00
    )

    # NULL until payment is made
    payment_date = models.DateTimeField(
        null=True,
        blank=True
    )

    # Unique receipt reference
    receipt_number = models.CharField(
        max_length=20,
        unique=True,
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'payment_table'
        verbose_name = 'Payment'
        verbose_name_plural = 'Payments'

    def __str__(self):
        return (
            f"Payment #{self.payment_id} - "
            f"{self.student.full_name}"
        )
