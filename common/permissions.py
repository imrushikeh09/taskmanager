from rest_framework import permissions
from common.roles import UserRole, get_user_role


class RBACPermission(permissions.BasePermission):
    """
    Role-Based Access Control (RBAC) & Object Ownership Permission (Day 14):
    - ADMIN: Full management access across all resources (read, write, update, delete).
    - CONTRIBUTOR: Standard member. Can view all resources, create resources,
      and update/delete ONLY the resources they personally created or own.
    - VIEWER: Strictly read-only (GET, HEAD, OPTIONS). All mutations return 403 Forbidden.
    - UNAUTHENTICATED: Safe methods allowed; all mutations return 401 Unauthorized.
    """

    def has_permission(self, request, view):
        """Evaluate view-level permissions and role mutation privileges."""
        # Safe methods (GET, HEAD, OPTIONS) are allowed to all clients
        if request.method in permissions.SAFE_METHODS:
            return True

        # Mutation methods require authentication (returns 401 if unauthenticated)
        if not (request.user and request.user.is_authenticated):
            return False

        # Role Check: Viewers are strictly prohibited from write operations
        role = get_user_role(request.user)
        if role == UserRole.VIEWER:
            return False

        # Admins and Contributors are permitted to submit mutations
        return True

    def has_object_permission(self, request, view, obj):
        """Evaluate object-level ownership boundaries and Admin overrides."""
        # Safe methods (GET, HEAD, OPTIONS) are permitted
        if request.method in permissions.SAFE_METHODS:
            return True

        # Admins have master override permissions on any object
        role = get_user_role(request.user)
        if role == UserRole.ADMIN:
            return True

        # Viewers cannot modify objects
        if role == UserRole.VIEWER:
            return False

        # Contributors can only modify resources they personally own or created
        # Check Project ownership
        if hasattr(obj, "owner"):
            return obj.owner == request.user

        # Check Task ownership (task creator OR parent project owner)
        if hasattr(obj, "creator"):
            return obj.creator == request.user or (hasattr(obj, "project") and obj.project.owner == request.user)

        return False


# Backward compatibility alias
IsOwnerOrReadOnly = RBACPermission

