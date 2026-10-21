from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Object-level permission allowing read-only access for any authenticated user,
    but restricting write/delete operations exclusively to the resource owner/creator.
    Returns 401 if unauthenticated and 403 if authenticated but not the owner.
    """

    def has_permission(self, request, view):
        """Allow read-only requests or require authentication for modifications."""
        if request.method in permissions.SAFE_METHODS:
            return True
        return bool(request.user and request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """Grant write access only to the owner or creator of the object."""
        # Read-only methods (GET, HEAD, OPTIONS) are permitted
        if request.method in permissions.SAFE_METHODS:
            return True

        # Check for 'owner' field (e.g. Project)
        if hasattr(obj, "owner"):
            return obj.owner == request.user

        # Check for 'creator' field (e.g. Task)
        if hasattr(obj, "creator"):
            # Task creator OR project owner has permission
            return obj.creator == request.user or (hasattr(obj, "project") and obj.project.owner == request.user)

        return False
