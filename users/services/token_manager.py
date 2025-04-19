from datetime import datetime, timedelta
from django.conf import settings
from django.core.cache import cache
from cryptography.fernet import Fernet
import jwt
import logging
from typing import Dict, Optional, Tuple

logger = logging.getLogger('oauth')

class TokenManager:
    def __init__(self):
        # Initialize encryption key from settings or generate new one
        self.fernet = Fernet(settings.TOKEN_ENCRYPTION_KEY.encode())
        # Minimum time before expiry to trigger rotation (30 minutes)
        self.rotation_threshold = timedelta(minutes=30)
        
    def encrypt_token(self, token: str) -> str:
        """Encrypt a token before storage."""
        return self.fernet.encrypt(token.encode()).decode()
        
    def decrypt_token(self, encrypted_token: str) -> str:
        """Decrypt a stored token."""
        return self.fernet.decrypt(encrypted_token.encode()).decode()
        
    def store_tokens(self, user_id: int, platform: str, tokens: Dict[str, str], 
                    expires_in: int) -> None:
        """
        Store encrypted tokens with expiry information.
        
        Args:
            user_id: The user's ID
            platform: Social media platform
            tokens: Dict containing access_token and refresh_token
            expires_in: Token expiry time in seconds
        """
        expiry_date = datetime.now() + timedelta(seconds=expires_in)
        
        encrypted_data = {
            'access_token': self.encrypt_token(tokens['access_token']),
            'refresh_token': self.encrypt_token(tokens.get('refresh_token', '')),
            'expiry_date': expiry_date.isoformat(),
            'platform': platform
        }
        
        # Store in user's social account field
        user = User.objects.get(id=user_id)
        account_field = f"{platform}_account"
        setattr(user, account_field, encrypted_data)
        user.save()
        
        # Set cache for quick access token lookup
        cache_key = f"token_{user_id}_{platform}"
        cache.set(cache_key, encrypted_data, timeout=expires_in)
        
        logger.info(f"Stored tokens for user {user_id} on {platform}", 
                   extra={'user_id': user_id, 'platform': platform})
                   
    def get_valid_token(self, user_id: int, platform: str) -> Tuple[str, bool]:
        """
        Get a valid access token, rotating if necessary.
        
        Returns:
            Tuple[str, bool]: (access_token, was_rotated)
        """
        cache_key = f"token_{user_id}_{platform}"
        encrypted_data = cache.get(cache_key)
        
        if not encrypted_data:
            # Load from database if not in cache
            user = User.objects.get(id=user_id)
            account_field = f"{platform}_account"
            encrypted_data = getattr(user, account_field)
            if not encrypted_data:
                raise TokenError(f"No tokens found for {platform}")
        
        expiry_date = datetime.fromisoformat(encrypted_data['expiry_date'])
        access_token = self.decrypt_token(encrypted_data['access_token'])
        
        # Check if token needs rotation
        if datetime.now() + self.rotation_threshold > expiry_date:
            try:
                access_token, rotated = self._rotate_token(user_id, platform, encrypted_data)
                if rotated:
                    return access_token, True
            except Exception as e:
                logger.error(f"Token rotation failed: {str(e)}", 
                           extra={'user_id': user_id, 'platform': platform})
                # Continue with current token if rotation fails
                
        return access_token, False
        
    def _rotate_token(self, user_id: int, platform: str, 
                     encrypted_data: Dict) -> Tuple[str, bool]:
        """
        Attempt to rotate tokens using refresh token if available.
        
        Returns:
            Tuple[str, bool]: (access_token, was_rotated)
        """
        refresh_token = self.decrypt_token(encrypted_data['refresh_token'])
        if not refresh_token:
            return self.decrypt_token(encrypted_data['access_token']), False
            
        try:
            # Get platform-specific token refresh function
            refresh_func = self._get_refresh_function(platform)
            new_tokens = refresh_func(refresh_token)
            
            # Store new tokens
            self.store_tokens(
                user_id=user_id,
                platform=platform,
                tokens=new_tokens,
                expires_in=new_tokens.get('expires_in', 3600)
            )
            
            logger.info(f"Rotated tokens for user {user_id} on {platform}", 
                       extra={'user_id': user_id, 'platform': platform})
            return new_tokens['access_token'], True
            
        except Exception as e:
            logger.error(f"Token refresh failed: {str(e)}", 
                        extra={'user_id': user_id, 'platform': platform})
            raise TokenRefreshError(f"Failed to refresh {platform} token: {str(e)}")
            
    def _get_refresh_function(self, platform: str):
        """Get the appropriate refresh function for the platform."""
        from .oauth import (
            refresh_google_token,
            refresh_facebook_token,
            refresh_linkedin_token,
            refresh_twitter_token,
            refresh_instagram_token,
            refresh_tiktok_token
        )
        
        refresh_functions = {
            'google': refresh_google_token,
            'facebook': refresh_facebook_token,
            'linkedin': refresh_linkedin_token,
            'twitter': refresh_twitter_token,
            'instagram': refresh_instagram_token,
            'tiktok': refresh_tiktok_token
        }
        
        return refresh_functions.get(platform)
        
    def revoke_tokens(self, user_id: int, platform: str) -> None:
        """Revoke and remove stored tokens."""
        user = User.objects.get(id=user_id)
        account_field = f"{platform}_account"
        
        # Get encrypted tokens
        encrypted_data = getattr(user, account_field)
        if encrypted_data:
            try:
                # Attempt to revoke tokens with platform
                access_token = self.decrypt_token(encrypted_data['access_token'])
                self._revoke_platform_tokens(platform, access_token)
            except Exception as e:
                logger.warning(f"Token revocation failed: {str(e)}", 
                             extra={'user_id': user_id, 'platform': platform})
        
        # Clear stored tokens
        setattr(user, account_field, None)
        user.save()
        
        # Clear cache
        cache_key = f"token_{user_id}_{platform}"
        cache.delete(cache_key)
        
        logger.info(f"Revoked tokens for user {user_id} on {platform}", 
                   extra={'user_id': user_id, 'platform': platform})
                   
    def _revoke_platform_tokens(self, platform: str, access_token: str) -> None:
        """Platform-specific token revocation."""
        # Implement platform-specific revocation logic here
        pass


class TokenError(Exception):
    """Base exception for token-related errors."""
    pass

class TokenRefreshError(TokenError):
    """Error during token refresh."""
    pass 