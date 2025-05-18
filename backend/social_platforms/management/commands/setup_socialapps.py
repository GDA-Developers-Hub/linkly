"""
Management command to register social apps with Django AllAuth.
This ensures the existing OAuth credentials are properly set up with AllAuth.
"""
import logging
from django.core.management.base import BaseCommand
from django.db import transaction
from allauth.socialaccount.models import SocialApp
from django.contrib.sites.models import Site
from social_platforms.models import SocialPlatform

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Sets up SocialApp entries for Django AllAuth based on existing SocialPlatform entries'

    def handle(self, *args, **options):
        # Make sure we have a site
        site, created = Site.objects.get_or_create(id=1)
        if created:
            site.domain = 'localhost:8000'
            site.name = 'Linkly'
            site.save()
            self.stdout.write(self.style.SUCCESS(f'Created default site: {site.name}'))
        
        # Map our platform names to AllAuth provider names
        provider_map = {
            'facebook': 'facebook',
            'instagram': 'instagram',
            'twitter': 'twitter',
            'linkedin': 'linkedin_oauth2',
            'youtube': 'google',  # YouTube uses Google OAuth
            'google': 'google',   # For Google Analytics/Ads
            'pinterest': None,    # Not supported by AllAuth out of box
            'threads': 'instagram'  # Threads uses Instagram/Meta Auth
        }
        
        # Get all active platforms
        platforms = SocialPlatform.objects.filter(is_active=True)
        self.stdout.write(f'Found {platforms.count()} active social platforms')
        
        # Create social apps for each platform
        for platform in platforms:
            provider = provider_map.get(platform.name)
            
            if not provider:
                self.stdout.write(self.style.WARNING(
                    f'Platform {platform.name} does not have a corresponding AllAuth provider. Skipping.'
                ))
                continue
            
            try:
                with transaction.atomic():
                    # Create or update the SocialApp
                    social_app, created = SocialApp.objects.update_or_create(
                        provider=provider,
                        defaults={
                            'name': platform.display_name or platform.name.capitalize(),
                            'client_id': platform.client_id,
                            'secret': platform.client_secret,
                            'key': '',  # Required field by AllAuth but not used for OAuth2
                        }
                    )
                    
                    # Make sure it's associated with our site
                    social_app.sites.add(site)
                    
                    if created:
                        action = "Created"
                    else:
                        action = "Updated"
                        
                    self.stdout.write(self.style.SUCCESS(
                        f'{action} social app for {platform.name} (AllAuth provider: {provider})'
                    ))
            
            except Exception as e:
                self.stdout.write(self.style.ERROR(
                    f'Error creating social app for {platform.name}: {str(e)}'
                ))
        
        self.stdout.write(self.style.SUCCESS('Social apps setup completed'))
