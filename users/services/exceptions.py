class OAuthError(Exception):
    """Base exception for OAuth related errors."""
    pass

class TokenExchangeError(OAuthError):
    """Raised when token exchange fails."""
    pass

class StateVerificationError(OAuthError):
    """Raised when state verification fails."""
    pass

class PKCEVerificationError(OAuthError):
    """Raised when PKCE verification fails."""
    pass

class ProfileFetchError(OAuthError):
    """Raised when fetching user profile fails."""
    pass

class BusinessAccountError(OAuthError):
    """Raised when business account connection fails."""
    pass

class SocialConnectionError(OAuthError):
    """Exception raised when social account connection fails"""
    pass

class TokenRefreshError(OAuthError):
    """Exception raised when token refresh fails"""
    pass 