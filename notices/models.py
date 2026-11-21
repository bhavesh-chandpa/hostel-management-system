from django.db import models


class Notice(models.Model):

    # Primary key
    notice_id = models.AutoField(primary_key=True)

    # Notice heading
    title = models.CharField(max_length=50)

    # Notice body
    content = models.TextField()

    # Staff member who posted the notice
    posted_by = models.ForeignKey(
        'accounts.Staff',
        on_delete=models.PROTECT,
        db_column='posted_by',
        related_name='posted_notices'
    )

    # Automatically records publication time
    posted_at = models.DateTimeField(auto_now_add=True)

    # True = Active, False = Deactivated
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'notice_table'
        verbose_name = 'Notice'
        verbose_name_plural = 'Notices'

    def __str__(self):
        return self.title
