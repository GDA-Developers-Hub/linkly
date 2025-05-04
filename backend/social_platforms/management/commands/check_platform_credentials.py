from django.core.management.base import BaseCommand
from social_platforms.models import SocialPlatform
import json

class Command(BaseCommand):
    help = 'Check and display all social platform credentials'

    def handle(self, *args, **options):
        platforms = SocialPlatform.objects.all()
        
        if not platforms.exists():
            self.stdout.write(self.style.ERROR('No social platforms found in the database.'))
            return
            
        self.stdout.write(self.style.SUCCESS(f'Found {platforms.count()} social platforms:'))
        self.stdout.write('=' * 80)
        
        for platform in platforms:
            self.stdout.write(self.style.SUCCESS(f'Platform: {platform.display_name} ({platform.name})'))
            self.stdout.write(f'Client ID: {platform.client_id}')
            self.stdout.write(f'Auth URL: {platform.auth_url}')
            self.stdout.write(f'Redirect URI: {platform.redirect_uri}')
            self.stdout.write(f'Scope: {platform.scope}')
            self.stdout.write('=' * 80) 