from rest_framework import permissions


class AllowUnAuthenticated(permissions.BasePermission):
    """
    Allow unauthenticated access.
    """
    def has_permission(self, request, view):
        return True
