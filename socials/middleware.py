# social/middleware.py

import time
from django.utils import timezone
from .models import APIUsageLog, APIQuota

class APIUsageMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        
        if hasattr(request, 'user') and request.user.is_authenticated:
            # Only track API endpoints
            if request.path.startswith('/api/'):
                platform = self.determine_platform(request.path)
                if platform:
                    duration = time.time() - start_time
                    
                    # Log the API usage
                    APIUsageLog.objects.create(
                        user=request.user,
                        platform=platform,
                        endpoint=request.path,
                        status=response.status_code,
                        response_time=duration
                    )
                    
                    # Update quota
                    quota, _ = APIQuota.objects.get_or_create(
                        user=request.user,
                        platform=platform,
                        defaults={
                            'limit': self.get_platform_limit(request.user, platform),
                            'reset_at': self.get_next_reset_time()
                        }
                    )
                    
                    # Reset quota if needed
                    if timezone.now() >= quota.reset_at:
                        quota.used = 0
                        quota.reset_at = self.get_next_reset_time()
                    
                    quota.used += 1
                    quota.save()
        
        return response

    @staticmethod
    def determine_platform(path):
        if 'instagram' in path:
            return 'instagram'
        elif 'facebook' in path:
            return 'facebook'
        elif 'twitter' in path:
            return 'twitter'
        elif 'linkedin' in path:
            return 'linkedin'
        return None

    @staticmethod
    def get_platform_limit(user, platform):
        # Get limit based on user's subscription plan
        subscription = user.current_subscription
        if not subscription:
            return 50  # Default limit
            
        plan_limits = {
            'FREE_TRIAL': 50,
            'STARTER': 100,
            'PRO': 200,
            'ENTERPRISE': 500
        }
        
        return plan_limits.get(subscription.plan.name, 50)

    @staticmethod
    def get_next_reset_time():
        # Reset at midnight
        now = timezone.now()
        return (now + timedelta(days=1)).replace(
            hour=0, minute=0, second=0, microsecond=0
        )