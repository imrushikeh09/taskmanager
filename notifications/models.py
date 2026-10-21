from django.conf import settings
from django.db import models
from common.models import TimeStampedModel
from .choices import NotificationType


class Notification(TimeStampedModel):
    """
    In-app alert delivered to users for critical system and domain events.
    Indexed on (recipient, is_read) for instant lookup of unread notifications.
    """
    recipient = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="notifications",
        help_text="Recipient of the in-app notification",
    )
    task = models.ForeignKey(
        "tasks.Task",
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name="notifications",
        help_text="Associated task reference, if applicable",
    )
    notification_type = models.CharField(
        max_length=50,
        choices=NotificationType.choices,
        help_text="Classification of notification event",
    )
    message = models.TextField(help_text="Human-readable notification text")
    is_read = models.BooleanField(
        default=False,
        help_text="Indicates if recipient has acknowledged/read the notification",
    )

    class Meta:
        db_table = "notifications"
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["recipient", "is_read"], name="idx_notif_recipient_read"),
        ]

    def __str__(self):
        return f"Notification to user={self.recipient_id} [{self.notification_type}] (read={self.is_read})"
