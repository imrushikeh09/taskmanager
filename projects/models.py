from django.conf import settings
from django.db import models


class Project(models.Model):
    """
    Represents a project workspace owned by a user.
    Contains tasks and defines boundaries for team access.
    """
    name = models.CharField(max_length=150, help_text="Name of the project")
    description = models.TextField(blank=True, default="", help_text="Detailed description of the project")
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="owned_projects",
        help_text="User who owns and manages the project",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = "projects"
        ordering = ["-created_at"]
        constraints = [
            models.UniqueConstraint(
                fields=["owner", "name"],
                name="unique_project_owner_name",
            )
        ]

    def __str__(self):
        return self.name
