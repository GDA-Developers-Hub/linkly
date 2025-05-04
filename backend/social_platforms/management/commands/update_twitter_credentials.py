from django.core.management.base import BaseCommand
from social_platforms.models import SocialPlatform

class Command(BaseCommand):
    help = 'Update Twitter platform credentials with real values'

    def add_arguments(self, parser):
        parser.add_argument('--client-id', type=str, help='Twitter client ID')
        parser.add_argument('--client-secret', type=str, help='Twitter client secret')

    def handle(self, *args, **options):
        client_id = options.get('client_id')
        client_secret = options.get('client_secret')
        
        # Use realistic sample values if not provided
        if not client_id:
            client_id = "a1b2c3d4e5f6g7h8i9j0"  # This is a placeholder, use your actual Twitter API client ID
        
        if not client_secret:
            client_secret = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789"  # Placeholder
        
        try:
            twitter = SocialPlatform.objects.get(name='twitter')
            
            # Keep original values for reference
            old_client_id = twitter.client_id
            
            # Update the values
            twitter.client_id = client_id
            twitter.client_secret = client_secret
            twitter.save()
            
            self.stdout.write(self.style.SUCCESS(f'Successfully updated Twitter credentials'))
            self.stdout.write(f'Old client ID: {old_client_id}')
            self.stdout.write(f'New client ID: {client_id}')
            
        except SocialPlatform.DoesNotExist:
            self.stdout.write(self.style.ERROR('Twitter platform not found in the database')) 