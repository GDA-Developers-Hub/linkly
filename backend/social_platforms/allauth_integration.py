"""
Integration utilities for Django Allauth and Linkly's social platform connections.
"""
import os
import logging
from django.urls import reverse
from django.conf import settings
from allauth.socialaccount.models import SocialApp
from allauth.socialaccount.providers.oauth2.views import OAuth2Adapter

logger = logging.getLogger(__name__)

def get_oauth_redirect_url(request, provider_id):
    """
    Get the OAuth redirect URL for a specific provider.
    
    Args:
        request: Django request object
        provider_id: String ID of the provider (e.g., 'facebook', 'tiktok')
        
    Returns:
        dict: Dictionary with authorization URL and state
    """
    try:
        # Get provider module
        provider_module = __import__(
            f'allauth.socialaccount.providers.{provider_id}.provider',
            fromlist=['provider']
        )
        Provider = provider_module.provider_classes[0]
        provider = Provider()
        
        # For custom providers, we need a different import path
        if provider_id in ['tiktok', 'youtube', 'threads', 'pinterest', 'google_ads']:
            adapter_module = __import__(
                f'social_platforms.providers.{provider_id}.views',
                fromlist=['views']
            )
        else:
            adapter_module = __import__(
                f'allauth.socialaccount.providers.{provider_id}.views',
                fromlist=['views']
            )
        
        # Find the adapter class
        adapter_class = None
        for name in dir(adapter_module):
            obj = getattr(adapter_module, name)
            if isinstance(obj, type) and issubclass(obj, OAuth2Adapter) and obj != OAuth2Adapter:
                adapter_class = obj
                break
        
        if not adapter_class:
            raise Exception(f"Could not find OAuth2Adapter for provider {provider_id}")
        
        adapter = adapter_class()
        
        # Get the SocialApp for this provider
        app = SocialApp.objects.get(provider=provider_id)
        
        # Build the authorize URL with required parameters
        redirect_uri = request.build_absolute_uri(
            reverse(f'{provider_id}_callback')
        )
        
        # Generate the authorization URL
        authorize_url = adapter.authorize_url
        scope = ' '.join(provider.get_default_scope())
        
        # Generate a random state
        import secrets
        state = secrets.token_urlsafe(32)
        
        # Store the state in the session
        request.session[f'{provider_id}_oauth_state'] = state
        
        # Construct the full authorization URL
        params = {
            'client_id': app.client_id,
            'redirect_uri': redirect_uri,
            'response_type': 'code',
            'scope': scope,
            'state': state
        }
        
        from urllib.parse import urlencode
        auth_url = f"{authorize_url}?{urlencode(params)}"
        
        return {
            'authorization_url': auth_url,
            'state': state
        }
    
    except Exception as e:
        logger.exception(f"Error generating OAuth URL for {provider_id}: {str(e)}")
        return {
            'error': str(e)
        }

def initialize_social_apps():
    """
    Initialize SocialApp instances for all configured providers in settings.
    This should be called during app startup to ensure all providers are registered.
    """
    from django.contrib.sites.models import Site
    from allauth.socialaccount.models import SocialApp
    
    # Get the current site
    site = Site.objects.get_current()
    
    # For each provider in SOCIALACCOUNT_PROVIDERS, check if we have a social app
    for provider_id, config in settings.SOCIALACCOUNT_PROVIDERS.items():
        # First check if a SocialApp already exists for this provider
        existing_app = SocialApp.objects.filter(provider=provider_id).first()
        
        if existing_app:
            # Make sure the app is associated with the current site
            if site not in existing_app.sites.all():
                existing_app.sites.add(site)
                existing_app.save()
                logger.info(f"Added site to existing SocialApp for {provider_id}")
            continue
            
        # If no existing app, try to create one from environment variables
        client_id_env = f"{provider_id.upper()}_CLIENT_ID"
        client_secret_env = f"{provider_id.upper()}_CLIENT_SECRET"
        
        # Use getattr to safely access settings or fall back to environment variables
        client_id = getattr(settings, client_id_env, None) or os.environ.get(client_id_env)
        client_secret = getattr(settings, client_secret_env, None) or os.environ.get(client_secret_env)
        
        if not client_id or not client_secret:
            logger.debug(f"No environment credentials for {provider_id}, skipping automatic SocialApp creation")
            continue
        
        # Create or update the SocialApp
        app, created = SocialApp.objects.update_or_create(
            provider=provider_id,
            defaults={
                'name': provider_id.title(),
                'client_id': client_id,
                'secret': client_secret,
                'key': ''  # Not used for OAuth2
            }
        )
        
        # Ensure the app is associated with the current site
        app.sites.add(site)
        
        if created:
            logger.info(f"Created SocialApp for {provider_id}")
        else:
            logger.info(f"Updated SocialApp for {provider_id}")
