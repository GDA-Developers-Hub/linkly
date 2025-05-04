from django.core.management.base import BaseCommand
from social_platforms.models import SocialPlatform

class Command(BaseCommand):
    help = 'Check Twitter platform credentials'

    def handle(self, *args, **options):
        try:
            twitter = SocialPlatform.objects.get(name='twitter')
            
            self.stdout.write(self.style.SUCCESS(f'Twitter platform details:'))
            self.stdout.write(f'Name: {twitter.display_name}')
            self.stdout.write(f'Client ID: {twitter.client_id}')
            self.stdout.write(f'Client Secret: {twitter.client_secret[:5]}...{twitter.client_secret[-5:]}')
            self.stdout.write(f'Auth URL: {twitter.auth_url}')
            self.stdout.write(f'Token URL: {twitter.token_url}')
            self.stdout.write(f'Redirect URI: {twitter.redirect_uri}')
            self.stdout.write(f'Scope: {twitter.scope}')
            self.stdout.write(f'Active: {twitter.is_active}')
            
        except SocialPlatform.DoesNotExist:
            self.stdout.write(self.style.ERROR('Twitter platform not found in the database')) 