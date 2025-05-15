"""
Custom adapters for Django AllAuth to integrate with Linkly's social platform connections.
"""
import logging
from allauth.socialaccount.adapter import DefaultSocialAccountAdapter
from allauth.socialaccount.models import SocialToken
from django.utils import timezone
from .models import SocialPlatform, UserSocialAccount

logger = logging.getLogger(__name__)

class CustomSocialAccountAdapter(DefaultSocialAccountAdapter):
    """
    Custom social account adapter that integrates AllAuth with our existing UserSocialAccount model.
    This adapter ensures we maintain compatibility with the frontend while leveraging AllAuth's OAuth handling.
    """
    
    def save_user(self, request, sociallogin, form=None):
        """
        Save the user and create/update the corresponding UserSocialAccount record.
        This method is called by AllAuth after a successful social login.
        """
        # First, use AllAuth's default behavior to save the user
        user = super().save_user(request, sociallogin, form)
        
        try:
            # Extract data from the social account
            social_account = sociallogin.account
            provider = social_account.provider
            token = sociallogin.token
            extra_data = social_account.extra_data
            
            logger.info(f"Processing social login for provider: {provider}")
            
            # Map AllAuth provider names to our platform names if needed
            provider_mapping = {
                'google': 'youtube',  # For Google provider with YouTube scope
                'linkedin_oauth2': 'linkedin',
                'tiktok': 'tiktok',
                'youtube': 'youtube',
                'threads': 'threads',
                'pinterest': 'pinterest',
                'googleads': 'google_ads',
            }
            
            # Check if we need to handle a special case like YouTube via Google
            platform_name = provider
            if provider == 'google' and 'youtube' in getattr(token, 'scope', ''):
                platform_name = 'youtube'
                logger.info("Detected YouTube scope in Google OAuth")
            elif provider in provider_mapping:
                platform_name = provider_mapping[provider]
            
            # Get or create the platform
            try:
                platform = SocialPlatform.objects.get(name=platform_name)
            except SocialPlatform.DoesNotExist:
                logger.warning(f"Platform {platform_name} not found - fallback to provider {provider}")
                platform = SocialPlatform.objects.get(name=provider)
            
            # Extract profile data
            profile_data = self._extract_profile_data(provider, extra_data)
            
            # Get token data
            token_data = {
                'access_token': token.token,
                'token_type': getattr(token, 'token_type', 'Bearer'),
                'refresh_token': getattr(token, 'token_secret', None),  # OAuth 1.0 uses token_secret
                'expires_at': getattr(token, 'expires_at', None),
                'scope': getattr(token, 'scope', '')
            }
            
            # Create or update the UserSocialAccount
            account, created = UserSocialAccount.objects.update_or_create(
                user=user,
                platform=platform,
                account_id=social_account.uid,
                defaults={
                    'account_name': profile_data.get('name'),
                    'account_type': profile_data.get('account_type', 'profile'),
                    'profile_picture_url': profile_data.get('picture_url'),
                    'access_token': token_data['access_token'],
                    'refresh_token': token_data['refresh_token'],
                    'token_expiry': token_data['expires_at'],
                    'token_type': token_data['token_type'],
                    'scope': token_data['scope'],
                    'raw_data': extra_data,
                    'status': 'active',
                    'last_used_at': timezone.now()
                }
            )
            
            # If this is the first account for this platform, make it primary
            if created:
                if not UserSocialAccount.objects.filter(
                    user=user, 
                    platform=platform, 
                    is_primary=True
                ).exclude(id=account.id).exists():
                    account.is_primary = True
                    account.save()
            
            logger.info(f"Successfully created/updated {platform_name} account for user {user.id}")
            
            return user
            
        except Exception as e:
            logger.error(f"Error processing social login: {str(e)}")
            # We still want to return the user even if there was an error connecting the account
            return user
    
    def _extract_profile_data(self, provider, extra_data):
        """
        Extract standardized profile data from provider-specific extra_data.
        """
        profile_data = {
            'name': None,
            'picture_url': None,
            'account_type': 'profile'
        }
        
        if provider == 'facebook':
            profile_data['name'] = extra_data.get('name')
            if 'picture' in extra_data and 'data' in extra_data['picture']:
                profile_data['picture_url'] = extra_data['picture']['data'].get('url')
        
        elif provider == 'instagram':
            profile_data['name'] = extra_data.get('username')
            profile_data['account_type'] = extra_data.get('account_type', 'profile')
        
        elif provider == 'twitter':
            profile_data['name'] = extra_data.get('name')
            profile_data['picture_url'] = extra_data.get('profile_image_url')
        
        elif provider == 'linkedin_oauth2':
            # LinkedIn has a more complex structure
            profile_data['name'] = f"{extra_data.get('firstName', '')} {extra_data.get('lastName', '')}".strip()
            if 'profilePicture' in extra_data and 'displayImage' in extra_data['profilePicture']:
                profile_data['picture_url'] = extra_data['profilePicture']['displayImage']
        
        elif provider == 'google':
            profile_data['name'] = extra_data.get('name')
            profile_data['picture_url'] = extra_data.get('picture')
            
            # Check if this is Google with YouTube or Google Ads scope
            if 'is_google_ads_account' in extra_data:
                profile_data['account_type'] = 'ads'
        
        elif provider == 'youtube':
            # Direct YouTube provider
            profile_data['name'] = extra_data.get('channel_title') or extra_data.get('name')
            profile_data['picture_url'] = extra_data.get('profile_image_url') or extra_data.get('picture')
            profile_data['account_type'] = 'channel'
        
        elif provider == 'tiktok':
            profile_data['name'] = extra_data.get('display_name') or extra_data.get('username')
            profile_data['picture_url'] = extra_data.get('avatar_url')
            profile_data['account_type'] = 'tiktok'
        
        elif provider == 'threads':
            # Threads uses Instagram's API
            profile_data['name'] = extra_data.get('username')
            profile_data['picture_url'] = extra_data.get('profile_picture')
            profile_data['account_type'] = 'threads'
        
        elif provider == 'pinterest':
            profile_data['name'] = extra_data.get('username') or extra_data.get('full_name')
            profile_data['picture_url'] = extra_data.get('profile_image')
            profile_data['account_type'] = 'pinterest'
        
        elif provider == 'google_ads':
            profile_data['name'] = extra_data.get('name')
            profile_data['picture_url'] = extra_data.get('picture')
            profile_data['account_type'] = 'ads'
        
        return profile_data
