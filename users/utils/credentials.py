"""
Utility functions for handling platform credentials.
"""
from typing import Optional, Dict
from django.contrib.auth import get_user_model
from ..models import PlatformCredentials

User = get_user_model()

def get_user_platform_credentials(user_id: int, platform: str) -> Optional[Dict]:
    """
    Retrieve stored platform credentials for a specific user and platform.
    
    Args:
        user_id: The ID of the user
        platform: The platform identifier string
        
    Returns:
        Dict with client_id, client_secret, and redirect_uri if found, None otherwise
    """
    try:
        user = User.objects.get(id=user_id)
        credentials = PlatformCredentials.objects.get(user=user, platform=platform)
        
        return {
            'client_id': credentials.client_id,
            'client_secret': credentials.client_secret,
            'redirect_uri': credentials.redirect_uri
        }
        
    except (User.DoesNotExist, PlatformCredentials.DoesNotExist):
        return None

def has_custom_credentials(user_id: int, platform: str) -> bool:
    """
    Check if a user has custom credentials for a specific platform.
    
    Args:
        user_id: The ID of the user
        platform: The platform identifier string
        
    Returns:
        True if custom credentials exist, False otherwise
    """
    try:
        user = User.objects.get(id=user_id)
        return PlatformCredentials.objects.filter(user=user, platform=platform).exists()
    except User.DoesNotExist:
        return False 