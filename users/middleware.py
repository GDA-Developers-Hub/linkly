from django.http import JsonResponse
from django.urls import resolve
from rest_framework import status

class SubscriptionRestrictionMiddleware:
    """Middleware to enforce subscription restrictions"""

    def __call__(self, request):
        # Allow health checks to pass through
        if request.path == '/':
            return self.get_response(request)

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # List of paths that don't require subscription checks
        unrestricted_paths = [
            '/',
            'api/v1/users/subscriptions/checkout/',
            'api/v1/users/subscriptions/webhook/',
            'api/v1/users/subscriptions/status/',
            'api/v1/users/subscriptions/plans/',
            'api/v1/users/login/',
            'api/v1/users/register/',
            'api/v1/users/password-reset/',
            'api/v1/',
        ]

        # Check if the path is unrestricted
        if any(request.path.startswith(path) for path in unrestricted_paths):
            return self.get_response(request)

        # Skip subscription check for unauthenticated users
        if not request.user.is_authenticated:
            return self.get_response(request)

        # Get current subscription
        current_subscription = request.user.current_subscription

        # If no active subscription and not in unrestricted paths, return error
        if not current_subscription or not current_subscription.is_active():
            return JsonResponse({
                'error': 'Subscription required',
                'message': 'Please upgrade your subscription to access this feature.',
                'code': 'subscription_required'
            }, status=status.HTTP_402_PAYMENT_REQUIRED)

        # Check feature-specific restrictions
        url_name = resolve(request.path_info).url_name
        
        # Map URL patterns to required features
        feature_requirements = {
            'analytics': ['get-analytics', 'analytics-dashboard'],
            'advanced_analytics': ['advanced-analytics'],
            'content_calendar': ['calendar', 'schedule-post'],
            'team_collaboration': ['team', 'invite-member'],
            'competitor_analysis': ['competitor-analysis'],
            'api_access': ['api-token'],
        }

        # Check if the URL requires specific features
        for feature, urls in feature_requirements.items():
            if url_name in urls and not request.user.can_use_feature(feature):
                return JsonResponse({
                    'error': 'Feature not available',
                    'message': f'Please upgrade your subscription to access {feature.replace("_", " ")}.',
                    'code': 'feature_not_available'
                }, status=status.HTTP_402_PAYMENT_REQUIRED)

        # Check social accounts limit
        if url_name in ['connect-social-account', 'add-social-profile']:
            connected_accounts = sum([
                request.user.has_facebook_business,
                request.user.has_instagram_business,
                request.user.has_linkedin_company,
                request.user.has_youtube_brand,
                request.user.has_twitter_business,
                request.user.has_tiktok_business,
                request.user.has_telegram_channel,
            ])
            
            if connected_accounts >= current_subscription.plan.social_accounts_limit:
                return JsonResponse({
                    'error': 'Social accounts limit reached',
                    'message': 'You have reached the maximum number of social accounts for your current plan.',
                    'code': 'social_accounts_limit'
                }, status=status.HTTP_402_PAYMENT_REQUIRED)

        # Check AI caption limit
        if url_name == 'generate-caption':
            # TODO: Implement AI caption limit check based on usage tracking
            pass

        return self.get_response(request) 