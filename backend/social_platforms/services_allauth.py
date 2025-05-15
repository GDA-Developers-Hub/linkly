"""
Allauth-based services for social platform integration.
This file contains service functions that use Django Allauth for OAuth authentication.
"""
import logging
from django.utils import timezone
from allauth.socialaccount.models import SocialApp, SocialAccount, SocialToken
from .models import SocialPlatform, UserSocialAccount

logger = logging.getLogger(__name__)

def get_allauth_provider_for_platform(platform_name):
    """
    Map Linkly platform names to Allauth provider IDs.
    
    Args:
        platform_name: The platform name in our system
        
    Returns:
        The corresponding Allauth provider ID
    """
    platform_to_provider = {
        'linkedin': 'linkedin_oauth2',
        'google': 'google',
        'facebook': 'facebook',
        'instagram': 'instagram',
        'twitter': 'twitter',
        'tiktok': 'tiktok',
        'youtube': 'youtube',
        'threads': 'threads',
        'pinterest': 'pinterest',
        'google_ads': 'googleads',  # Updated provider ID
    }
    
    return platform_to_provider.get(platform_name, platform_name)

def sync_social_accounts(user):
    """
    Synchronize Allauth SocialAccounts with our UserSocialAccount model.
    
    Args:
        user: The user to synchronize accounts for
        
    Returns:
        dict: Results of the synchronization
    """
    # Get all Allauth social accounts for the user
    allauth_accounts = SocialAccount.objects.filter(user=user)
    
    results = {
        'created': 0,
        'updated': 0,
        'failed': 0,
        'accounts': []
    }
    
    for allauth_account in allauth_accounts:
        try:
            # Get the platform
            provider_id = allauth_account.provider
            
            # Map back to our platform name if needed
            provider_to_platform = {
                'linkedin_oauth2': 'linkedin',
                'google': 'google', 
            }
            platform_name = provider_to_platform.get(provider_id, provider_id)
            
            try:
                platform = SocialPlatform.objects.get(name=platform_name)
            except SocialPlatform.DoesNotExist:
                logger.warning(f"Platform {platform_name} not found")
                results['failed'] += 1
                continue
                
            # Get the token
            try:
                token = SocialToken.objects.get(account=allauth_account)
                token_data = {
                    'access_token': token.token,
                    'token_type': 'Bearer',
                    'refresh_token': token.token_secret,
                    'token_expiry': token.expires_at,
                }
            except SocialToken.DoesNotExist:
                token_data = {}
            
            # Get or create our UserSocialAccount
            account, created = UserSocialAccount.objects.update_or_create(
                user=user,
                platform=platform,
                account_id=allauth_account.uid,
                defaults={
                    'account_name': allauth_account.extra_data.get('name', ''),
                    'access_token': token_data.get('access_token', ''),
                    'refresh_token': token_data.get('refresh_token', ''),
                    'token_expiry': token_data.get('token_expiry'),
                    'token_type': token_data.get('token_type', 'Bearer'),
                    'raw_data': allauth_account.extra_data,
                    'status': 'active',
                    'last_used_at': timezone.now()
                }
            )
            
            if created:
                results['created'] += 1
            else:
                results['updated'] += 1
                
            results['accounts'].append({
                'id': account.id,
                'platform': platform.name,
                'account_name': account.account_name
            })
                
        except Exception as e:
            logger.exception(f"Error syncing account {allauth_account.id}: {str(e)}")
            results['failed'] += 1
    
    return results

def refresh_token_with_allauth(social_account):
    """
    Refresh an access token using Allauth's built-in refresh mechanism.
    
    Args:
        social_account: UserSocialAccount to refresh
        
    Returns:
        bool: Whether the refresh was successful
    """
    try:
        # Find the corresponding Allauth account
        allauth_account = SocialAccount.objects.get(
            user=social_account.user,
            uid=social_account.account_id,
            provider=get_allauth_provider_for_platform(social_account.platform.name)
        )
        
        # Get the token
        allauth_token = SocialToken.objects.get(account=allauth_account)
        
        # Use Allauth's refresh mechanism
        from allauth.socialaccount.helpers import complete_social_login
        from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter
        
        # Find the adapter for this provider
        provider_id = allauth_account.provider
        adapter = None
        
        # Import the appropriate adapter
        if provider_id in ['tiktok', 'youtube', 'threads', 'pinterest', 'google_ads']:
            module = __import__(
                f'social_platforms.providers.{provider_id}.views',
                fromlist=['views']
            )
        else:
            module = __import__(
                f'allauth.socialaccount.providers.{provider_id}.views',
                fromlist=['views']
            )
            
        # Find the adapter class
        for name in dir(module):
            obj = getattr(module, name)
            if isinstance(obj, type) and issubclass(obj, OAuth2Adapter) and obj != OAuth2Adapter:
                adapter_class = obj
                adapter = adapter_class()
                break
        
        if not adapter:
            logger.error(f"Could not find adapter for provider {provider_id}")
            return False
            
        # Refresh the token
        app = SocialApp.objects.get(provider=provider_id)
        new_token = adapter.refresh_token(allauth_token)
        
        # Update our UserSocialAccount with the new token data
        social_account.access_token = new_token.token
        social_account.refresh_token = new_token.token_secret
        social_account.token_expiry = new_token.expires_at
        social_account.last_used_at = timezone.now()
        social_account.save()
        
        return True
        
    except Exception as e:
        logger.exception(f"Error refreshing token with Allauth: {str(e)}")
        return False
