from django.conf import settings
from django.db import models


class TaskAttachment(models.Model):
    """
    Stores metadata for file attachments linked to a task.
    """
    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.CASCADE,
        related_name="attachments",
        help_text="Task this attachment belongs to",
    )
    uploader = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.PROTECT,
        related_name="uploaded_attachments",
        help_text="User who uploaded this file",
    )
    file_name = models.CharField(max_length=255, help_text="Original file name")
    file_url = models.CharField(max_length=500, help_text="Storage location or URL")
    file_size_bytes = models.BigIntegerField(help_text="File size in bytes")
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "task_attachments"
        ordering = ["-uploaded_at"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(file_size_bytes__gt=0),
                name="chk_attachment_file_size_positive",
            )
        ]

    def __str__(self):
        return f"{self.file_name} ({self.task.title})"
