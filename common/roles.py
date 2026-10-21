from django.db import models


class UserRole(models.TextChoices):
    """
    Standard RBAC Role Classifications (Day 14):
    - ADMIN: Full management over all tasks, projects, and users.
    - CONTRIBUTOR: Standard member; can create resources and modify own resources.
    - VIEWER: Read-only access; cannot create, update, or delete any resources.
    """
    ADMIN = "ADMIN", "Administrator"
    CONTRIBUTOR = "CONTRIBUTOR", "Contributor"
    VIEWER = "VIEWER", "Viewer"


def get_user_role(user) -> str:
    """
    Resolves the active RBAC role for a given user.
    Admins: is_superuser or is_staff or in 'Admin' group.
    Viewers: explicitly assigned to 'Viewer' group or viewer attribute.
    Contributors: default authenticated member.
    """
    if not user or not user.is_authenticated:
        return UserRole.VIEWER

    # Staff and Superusers automatically inherit the ADMIN role
    if user.is_superuser or user.is_staff or user.groups.filter(name=UserRole.ADMIN).exists():
        return UserRole.ADMIN

    # Explicit Viewer group membership
    if user.groups.filter(name=UserRole.VIEWER).exists():
        return UserRole.VIEWER

    # Default role for authenticated members
    return UserRole.CONTRIBUTOR
