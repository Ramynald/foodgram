"""Custom permissions for the API."""

from rest_framework.permissions import SAFE_METHODS, BasePermission


class IsAuthorOrReadOnly(BasePermission):
    """Allow authors to edit objects."""

    def has_permission(self, request, view):
        """Check general permission."""
        return request.method in SAFE_METHODS or request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """Check object permission."""
        return request.method in SAFE_METHODS or obj.author == request.user
