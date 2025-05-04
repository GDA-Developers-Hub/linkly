from django.core.management.base import BaseCommand
from social_platforms.models import SocialPlatform
from django.conf import settings
import os

class Command(BaseCommand):
    help = 'Set up social platforms for OAuth integration'
    
    def handle(self, *args, **options):
        # Common redirect URI for all platforms
        callback_url = 'http://localhost:8000/api/social_platforms/oauth/callback/'
        
        # Get settings from environment variables or settings module
        def get_setting(name, default=None):
            return getattr(settings, name, os.environ.get(name, default))
        
        # Instagram
        instagram_client_id = get_setting('INSTAGRAM_CLIENT_ID', 'demo-instagram-client-id')
        instagram_client_secret = get_setting('INSTAGRAM_CLIENT_SECRET', 'demo-instagram-client-secret')
        
        SocialPlatform.objects.update_or_create(
            name='instagram',
            defaults={
                'display_name': 'Instagram',
                'client_id': instagram_client_id,
                'client_secret': instagram_client_secret,
                'auth_url': 'https://api.instagram.com/oauth/authorize',
                'token_url': 'https://api.instagram.com/oauth/access_token',
                'redirect_uri': callback_url,
                'scope': 'user_profile user_media',
                'is_active': True
            }
        )
        self.stdout.write(self.style.SUCCESS('Successfully set up Instagram platform'))
        
        # Facebook
        facebook_app_id = get_setting('FACEBOOK_APP_ID', 'demo-facebook-app-id')
        facebook_app_secret = get_setting('FACEBOOK_APP_SECRET', 'demo-facebook-app-secret')
        
        SocialPlatform.objects.update_or_create(
            name='facebook',
            defaults={
                'display_name': 'Facebook',
                'client_id': facebook_app_id,
                'client_secret': facebook_app_secret,
                'auth_url': 'https://www.facebook.com/v16.0/dialog/oauth',
                'token_url': 'https://graph.facebook.com/v16.0/oauth/access_token',
                'redirect_uri': callback_url,
                'scope': 'public_profile,email,pages_show_list,pages_read_engagement,pages_manage_posts',
                'is_active': True
            }
        )
        self.stdout.write(self.style.SUCCESS('Successfully set up Facebook platform'))
        
        # Twitter (X)
        twitter_client_id = get_setting('TWITTER_CLIENT_ID', 'demo-twitter-client-id')
        twitter_client_secret = get_setting('TWITTER_CLIENT_SECRET', 'demo-twitter-client-secret')
        
        SocialPlatform.objects.update_or_create(
            name='twitter',
            defaults={
                'display_name': 'Twitter/X',
                'client_id': twitter_client_id,
                'client_secret': twitter_client_secret,
                'auth_url': 'https://twitter.com/i/oauth2/authorize',
                'token_url': 'https://api.twitter.com/2/oauth2/token',
                'redirect_uri': callback_url,
                'scope': 'tweet.read tweet.write users.read offline.access',
                'is_active': True
            }
        )
        self.stdout.write(self.style.SUCCESS('Successfully set up Twitter/X platform'))
        
        # LinkedIn
        linkedin_client_id = get_setting('LINKEDIN_CLIENT_ID', 'demo-linkedin-client-id')
        linkedin_client_secret = get_setting('LINKEDIN_CLIENT_SECRET', 'demo-linkedin-client-secret')
        
        SocialPlatform.objects.update_or_create(
            name='linkedin',
            defaults={
                'display_name': 'LinkedIn',
                'client_id': linkedin_client_id,
                'client_secret': linkedin_client_secret,
                'auth_url': 'https://www.linkedin.com/oauth/v2/authorization',
                'token_url': 'https://www.linkedin.com/oauth/v2/accessToken',
                'redirect_uri': callback_url,
                'scope': 'r_liteprofile r_emailaddress w_member_social',
                'is_active': True
            }
        )
        self.stdout.write(self.style.SUCCESS('Successfully set up LinkedIn platform'))
        
        # YouTube
        youtube_client_id = get_setting('YOUTUBE_CLIENT_ID', 'demo-youtube-client-id')
        youtube_client_secret = get_setting('YOUTUBE_CLIENT_SECRET', 'demo-youtube-client-secret')
        
        SocialPlatform.objects.update_or_create(
            name='youtube',
            defaults={
                'display_name': 'YouTube',
                'client_id': youtube_client_id,
                'client_secret': youtube_client_secret,
                'auth_url': 'https://accounts.google.com/o/oauth2/auth',
                'token_url': 'https://oauth2.googleapis.com/token',
                'redirect_uri': callback_url,
                'scope': 'https://www.googleapis.com/auth/youtube.readonly https://www.googleapis.com/auth/youtube.upload',
                'is_active': True
            }
        )
        self.stdout.write(self.style.SUCCESS('Successfully set up YouTube platform'))
        
        # TikTok
        tiktok_client_key = get_setting('TIKTOK_CLIENT_KEY', 'demo-tiktok-client-key')
        tiktok_client_secret = get_setting('TIKTOK_CLIENT_SECRET', 'demo-tiktok-client-secret')
        
        SocialPlatform.objects.update_or_create(
            name='tiktok',
            defaults={
                'display_name': 'TikTok',
                'client_id': tiktok_client_key,
                'client_secret': tiktok_client_secret,
                'auth_url': 'https://www.tiktok.com/auth/authorize/',
                'token_url': 'https://open-api.tiktok.com/oauth/access_token/',
                'redirect_uri': callback_url,
                'scope': 'user.info.basic video.list',
                'is_active': True
            }
        )
        self.stdout.write(self.style.SUCCESS('Successfully set up TikTok platform'))
        
        # Pinterest
        pinterest_client_id = get_setting('PINTEREST_APP_ID', 'demo-pinterest-app-id')
        pinterest_client_secret = get_setting('PINTEREST_APP_SECRET', 'demo-pinterest-app-secret')
        
        SocialPlatform.objects.update_or_create(
            name='pinterest',
            defaults={
                'display_name': 'Pinterest',
                'client_id': pinterest_client_id,
                'client_secret': pinterest_client_secret,
                'auth_url': 'https://www.pinterest.com/oauth/',
                'token_url': 'https://api.pinterest.com/v5/oauth/token',
                'redirect_uri': callback_url,
                'scope': 'boards:read,pins:read,pins:write',
                'is_active': True
            }
        )
        self.stdout.write(self.style.SUCCESS('Successfully set up Pinterest platform'))
        
        # Google Ads
        google_ads_client_id = get_setting('GOOGLE_ADS_CLIENT_ID', '507214707983-ubsf2ev7qkbcre4j4icsm8hvbq7id31a.apps.googleusercontent.com')
        google_ads_client_secret = get_setting('GOOGLE_ADS_CLIENT_SECRET', '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')
        
        SocialPlatform.objects.update_or_create(
            name='google',
            defaults={
                'display_name': 'Google Ads',
                'client_id': google_ads_client_id,
                'client_secret': google_ads_client_secret,
                'auth_url': 'https://accounts.google.com/o/oauth2/auth',
                'token_url': 'https://oauth2.googleapis.com/token',
                'redirect_uri': 'http://localhost:8000/auth/google/callback',
                'scope': 'https://www.googleapis.com/auth/adwords https://www.googleapis.com/auth/analytics.readonly',
                'is_active': True
            }
        )
        self.stdout.write(self.style.SUCCESS('Successfully set up Google Ads platform'))
        
        self.stdout.write(self.style.SUCCESS('All social platforms have been configured successfully!')) 