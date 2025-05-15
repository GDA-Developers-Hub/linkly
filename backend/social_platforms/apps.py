from django.apps import AppConfig
import logging

logger = logging.getLogger(__name__)

class SocialPlatformsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'social_platforms'
    
    def ready(self):
        """
        Initialize social platforms and custom Allauth providers when the app is ready.
        """
        from django.conf import settings
        from django.db import connection
        
        # Only initialize if database is available (skip during migrations)
        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
        except Exception as e:
            logger.warning(f"Database not available during app initialization: {str(e)}")
            return
        
        # Initialize all custom provider models
        try:
            from .models import SocialPlatform
            
            # Ensure all social platforms exist in the database
            platforms = [
                'facebook',
                'instagram',
                'twitter',
                'linkedin',
                'google',
                'youtube',
                'tiktok',
                'threads',
                'pinterest',
                'google_ads',
            ]
            
            for platform_name in platforms:
                SocialPlatform.objects.get_or_create(
                    name=platform_name,
                    defaults={
                        'display_name': platform_name.title(),
                        'is_active': True
                    }
                )
            
            logger.info("Social platforms initialized successfully")
            
            # Initialize Allauth social apps
            try:
                from .allauth_integration import initialize_social_apps
                initialize_social_apps()
                logger.info("Allauth social apps initialized successfully")
            except Exception as app_error:
                logger.warning(f"Could not initialize Allauth social apps: {str(app_error)}")
            
        except Exception as db_error:
            logger.warning(f"Error initializing social platforms: {str(db_error)}")
