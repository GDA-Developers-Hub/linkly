"""
Views package initialization.
This makes the views directory a proper Python package.
"""

from .auth import (
    RegisterView,
    CustomTokenObtainPairView,
    ChangePasswordView,
    ValidateTokenView
)
from .profile import (
    UpdateProfileView,
    UserProfileView
)
from .security import (
    Enable2FAView,
    Verify2FAView
)
from .subscription import (
    SubscriptionStatusView,
    available_plans,
    create_checkout_session
)
from .oauth import (
    init_oauth,
    oauth_callback,
    google_callback,
    facebook_callback,
    linkedin_callback,
    twitter_callback,
    instagram_callback,
    tiktok_callback,
    telegram_callback,
    unlink_social_account
)

__all__ = [
    'RegisterView',
    'CustomTokenObtainPairView',
    'ChangePasswordView',
    'ValidateTokenView',
    'UpdateProfileView',
    'UserProfileView',
    'Enable2FAView',
    'Verify2FAView',
    'SubscriptionStatusView',
    'available_plans',
    'create_checkout_session',
    'init_oauth',
    'oauth_callback',
    'google_callback',
    'facebook_callback',
    'linkedin_callback',
    'twitter_callback',
    'instagram_callback',
    'tiktok_callback',
    'telegram_callback',
    'unlink_social_account'
] 