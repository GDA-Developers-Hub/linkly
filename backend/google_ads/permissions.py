from rest_framework import permissions

class IsGoogleAdsManager(permissions.BasePermission):
    """
    Custom permission to only allow Google Ads managers to access the endpoints.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.groups.filter(name='google_ads_managers').exists()

class ReadOnlyUnlessManager(permissions.BasePermission):
    """
    Custom permission to allow read-only access to authenticated users,
    but full access to Google Ads managers.
    """
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
            
        # Allow read-only access to all authenticated users
        if request.method in permissions.SAFE_METHODS:
            return True
            
        # Allow full access to Google Ads managers
        return request.user.groups.filter(name='google_ads_managers').exists() 