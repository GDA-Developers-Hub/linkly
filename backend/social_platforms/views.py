from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from django.urls import reverse
from django.utils import timezone

from rest_framework import viewsets, permissions, status, views
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.exceptions import NotFound, ValidationError

import json
import logging
import uuid
import urllib.parse
import requests
from datetime import datetime, timedelta

from .models import SocialPlatform, UserSocialAccount
from .serializers import SocialPlatformSerializer, UserSocialAccountSerializer, SocialAccountDetailSerializer
from .services import get_oauth_manager, connect_social_account, refresh_token_if_needed

logger = logging.getLogger(__name__)

class SocialPlatformViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoints for viewing available social platforms
    """
    queryset = SocialPlatform.objects.filter(is_active=True)
    serializer_class = SocialPlatformSerializer
    permission_classes = [IsAuthenticated]
    

class UserSocialAccountViewSet(viewsets.ModelViewSet):
    """
    API endpoints for managing user's social media accounts
    """
    serializer_class = UserSocialAccountSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Return only the user's own social accounts"""
        return UserSocialAccount.objects.filter(user=self.request.user).select_related('platform')
    
    def get_serializer_class(self):
        """Return different serializers based on action"""
        if self.action == 'retrieve' or self.action == 'detail':
            return SocialAccountDetailSerializer
        return UserSocialAccountSerializer
    
    @action(detail=True, methods=['post'])
    def set_primary(self, request, pk=None):
        """Set an account as primary for its platform"""
        account = self.get_object()
        
        # Get all other accounts for the same platform and user
        UserSocialAccount.objects.filter(
            user=request.user,
            platform=account.platform,
            is_primary=True
        ).exclude(pk=account.pk).update(is_primary=False)
        
        # Set this account as primary
        account.is_primary = True
        account.save()
        
        return Response({'status': 'success', 'message': 'Account set as primary'})
    
    @action(detail=True, methods=['post'])
    def refresh_token(self, request, pk=None):
        """Refresh the token for this account if possible"""
        account = self.get_object()
        
        if not account.can_refresh:
            return Response(
                {'status': 'error', 'message': 'This account cannot refresh its token'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        success = refresh_token_if_needed(account)
        
        if success:
            return Response({'status': 'success', 'message': 'Token refreshed successfully'})
        else:
            return Response(
                {'status': 'error', 'message': 'Failed to refresh token'},
                status=status.HTTP_400_BAD_REQUEST
            )
    
    def destroy(self, request, *args, **kwargs):
        """Disconnect a social media account"""
        account = self.get_object()
        was_primary = account.is_primary
        platform = account.platform
        
        # Delete the account
        account.delete()
        
        # If this was a primary account, set another account as primary if available
        if was_primary:
            other_account = UserSocialAccount.objects.filter(
                user=request.user,
                platform=platform
            ).first()
            
            if other_account:
                other_account.is_primary = True
                other_account.save()
                
        return Response(status=status.HTTP_204_NO_CONTENT)


class OAuthInitView(views.APIView):
    """
    Initialize OAuth flow for a specific platform
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, platform):
        """Generate and return authorization URL"""
        try:
            # Log the request
            logger.info(f"OAuth init request for platform: {platform} from user: {request.user.email}")
            
            # Check if platform exists
            try:
                social_platform = SocialPlatform.objects.get(name=platform, is_active=True)
            except SocialPlatform.DoesNotExist:
                logger.error(f"Platform {platform} not found or not active")
                return Response(
                    {'error': f"Platform {platform} is not available"},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            # Generate unique state for CSRF protection
            state = str(uuid.uuid4())
            request.session[f'oauth_state_{platform}'] = state
            
            # Build the authorization URL using the platform's stored credentials
            auth_url = (
                f"{social_platform.auth_url}"
                f"?client_id={social_platform.client_id}"
                f"&redirect_uri={urllib.parse.quote(social_platform.redirect_uri)}"
                f"&response_type=code"
                f"&scope={urllib.parse.quote(social_platform.scope)}"
                f"&state={state}"
            )
            
            logger.info(f"Generated authorization URL for {platform}: {auth_url[:100]}...")
            
            return Response({
                'authorization_url': auth_url
            })
            
        except Exception as e:
            logger.error(f"Error initializing OAuth flow: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


class PublicOAuthInitView(views.APIView):
    """
    Initialize OAuth flow for a specific platform without requiring authentication
    This is a simplified version for demonstration purposes
    """
    permission_classes = [AllowAny]
    
    def get(self, request, platform):
        """Generate and return authorization URL"""
        try:
            # Log the request
            logger.info(f"Public OAuth init request for platform: {platform}")
            
            # Check if platform exists
            try:
                social_platform = SocialPlatform.objects.get(name=platform, is_active=True)
            except SocialPlatform.DoesNotExist:
                logger.error(f"Platform {platform} not found or not active")
                return Response(
                    {'error': f"Platform {platform} is not available"},
                    status=status.HTTP_404_NOT_FOUND
                )
                
            # Generate unique state for demo purposes
            state = "demo-state-" + str(uuid.uuid4())[:8]
            
            # Build the authorization URL using the platform's stored credentials
            auth_url = (
                f"{social_platform.auth_url}"
                f"?client_id={social_platform.client_id}"
                f"&redirect_uri={urllib.parse.quote(social_platform.redirect_uri)}"
                f"&response_type=code"
                f"&scope={urllib.parse.quote(social_platform.scope)}"
                f"&state={state}"
            )
            
            logger.info(f"Generated public authorization URL for {platform} with client ID: {social_platform.client_id[:10]}...")
            
            return Response({
                'authorization_url': auth_url
            })
            
        except Exception as e:
            logger.error(f"Error initializing public OAuth flow: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )


@method_decorator(login_required, name='dispatch')
class OAuthCallbackView(views.APIView):
    """
    Handle OAuth callback from social platforms
    """
    
    def get(self, request):
        """Process OAuth callback and create social account"""
        # Get parameters
        platform = request.GET.get('platform')
        code = request.GET.get('code')
        error = request.GET.get('error')
        state = request.GET.get('state')
        
        logger.info(f"OAuth callback received for platform: {platform}, code: {code[:5]}..., state: {state}")
        
        # Check for errors
        if error:
            logger.error(f"OAuth error: {error}")
            
            # For browser-based flows, return an HTML page that closes itself
            html_response = self.close_window(
                success=False,
                platform=platform,
                error=error
            )
            return HttpResponse(html_response)
            
        # Validate state for CSRF protection
        expected_state = request.session.get(f'oauth_state_{platform}')
        if not expected_state or expected_state != state:
            logger.error(f"OAuth state mismatch. Expected: {expected_state}, Got: {state}")
            
            # For browser-based flows, return an HTML page that closes itself
            html_response = self.close_window(
                success=False,
                platform=platform,
                error='Invalid state parameter'
            )
            return HttpResponse(html_response)
            
        # Clean up session
        if f'oauth_state_{platform}' in request.session:
            del request.session[f'oauth_state_{platform}']
            
        try:
            # Connect social account
            account = connect_social_account(request.user, platform, code)
            logger.info(f"Successfully connected {platform} account: {account.account_name}")
            
            # Return HTML response that will close the popup
            html_response = self.close_window(
                success=True,
                platform=platform,
                account_name=account.account_name
            )
            return HttpResponse(html_response)
            
        except Exception as e:
            logger.error(f"Error connecting account: {str(e)}")
            
            # For browser-based flows, return an HTML page that closes itself
            html_response = self.close_window(
                success=False,
                platform=platform,
                error=str(e)
            )
            return HttpResponse(html_response)
    
    def close_window(self, success=True, account_name=None, platform=None, error=None):
        """Return an HTML page that closes the popup window and sends a message to the opener"""
        context = {
            'success': success,
            'message': 'Account connected successfully' if success else f'Error: {error}',
            'account_name': account_name,
            'platform': platform,
            'error': error
        }
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{'Success' if success else 'Error'} - {platform} Authorization</title>
            <script>
                window.onload = function() {{
                    if (window.opener) {{
                        window.opener.postMessage(
                            JSON.stringify({json.dumps(context)}),
                            "*"
                        );
                        
                        // Add a small delay before closing the window
                        setTimeout(function() {{
                            window.close();
                        }}, 1500);
                    }} else {{
                        document.getElementById('message').style.display = 'block';
                    }}
                }};
            </script>
            <style>
                body {{ font-family: Arial, sans-serif; text-align: center; margin-top: 50px; }}
                .success {{ color: green; }}
                .error {{ color: red; }}
            </style>
        </head>
        <body>
            <div id="message" style="display:none; text-align:center; margin-top:50px;">
                <h3 class="{'success' if success else 'error'}">{'Success!' if success else 'Error'}</h3>
                <p>{context['message']}</p>
                <p>You can close this window now.</p>
            </div>
            <div id="auto-message" style="text-align:center; margin-top:50px;">
                <h3 class="{'success' if success else 'error'}">{'Success!' if success else 'Error'}</h3>
                <p>{context['message']}</p>
                <p>This window will close automatically...</p>
            </div>
        </body>
        </html>
        """
        
        return html


class SocialAccountPostView(views.APIView):
    """
    Post content to social media accounts
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None):
        """Create a post on social media platforms"""
        # Get post data
        post_data = request.data
        
        # Validate data
        if not post_data.get('text') and not post_data.get('media_urls'):
            return Response(
                {'error': 'Post must contain text or media'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Get target platforms
        platform_ids = post_data.get('platform_ids', [])
        account_ids = post_data.get('account_ids', [])
        
        if not platform_ids and not account_ids:
            return Response(
                {'error': 'Must specify at least one platform or account'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Get accounts to post to
        accounts = []
        
        # If specific accounts provided
        if account_ids:
            accounts.extend(
                UserSocialAccount.objects.filter(
                    id__in=account_ids,
                    user=request.user,
                    status='active'
                )
            )
            
        # If platforms provided, use primary accounts
        if platform_ids:
            platform_accounts = UserSocialAccount.objects.filter(
                platform_id__in=platform_ids,
                user=request.user,
                is_primary=True,
                status='active'
            )
            accounts.extend(platform_accounts)
            
        if not accounts:
            return Response(
                {'error': 'No valid accounts found for the specified platforms'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Initialize results
        results = []
        
        # Post to each account
        for account in accounts:
            try:
                # Refresh token if needed
                if account.is_expired:
                    if not refresh_token_if_needed(account):
                        results.append({
                            'account_id': account.id,
                            'platform': account.platform.name,
                            'success': False,
                            'error': 'Token expired and could not be refreshed'
                        })
                        continue
                
                # Platform-specific posting logic would be implemented here
                # For now we'll just record the attempt
                
                # Update account usage timestamp
                account.last_used_at = timezone.now()
                account.save()
                
                results.append({
                    'account_id': account.id,
                    'platform': account.platform.name,
                    'success': True,
                    'post_id': 'mock_post_id',  # This would be the actual post ID from the platform
                })
                
            except Exception as e:
                logger.error(f"Error posting to {account.platform.name}: {str(e)}")
                results.append({
                    'account_id': account.id,
                    'platform': account.platform.name,
                    'success': False,
                    'error': str(e)
                })
                
        return Response({
            'results': results
        })


@method_decorator(login_required, name='dispatch')
class GoogleOAuthCallbackView(views.APIView):
    """
    Handle OAuth callback specifically for Google services
    """
    
    def get(self, request):
        """Process Google OAuth callback and create social account"""
        # Get parameters
        code = request.GET.get('code')
        error = request.GET.get('error')
        state = request.GET.get('state')
        
        # Default platform (since this is specific to Google)
        platform = 'google'
        
        # Check for errors
        if error:
            logger.error(f"Google OAuth error: {error}")
            return self.close_window(success=False, error=error)
            
        # Validate state for CSRF protection if available
        expected_state = request.session.get(f'oauth_state_{platform}')
        if state and expected_state and expected_state != state:
            logger.error(f"OAuth state mismatch. Expected: {expected_state}, Got: {state}")
            return self.close_window(success=False, error='Invalid state parameter')
            
        # Clean up session
        if f'oauth_state_{platform}' in request.session:
            del request.session[f'oauth_state_{platform}']
            
        try:
            # Connect social account
            account = connect_social_account(request.user, platform, code)
            
            # Return success response
            return self.close_window(
                success=True,
                account_name=account.account_name,
                platform=platform
            )
            
        except Exception as e:
            logger.error(f"Error connecting Google account: {str(e)}")
            return self.close_window(success=False, error=str(e))
    
    def close_window(self, success=True, account_name=None, platform=None, error=None):
        """Return an HTML page that closes the popup window and sends a message to the opener"""
        context = {
            'success': success,
            'message': 'Account connected successfully' if success else f'Error: {error}',
            'account_name': account_name,
            'platform': platform,
            'error': error
        }
        
        html = f"""
        <!DOCTYPE html>
        <html>
        <head>
            <title>{'Success' if success else 'Error'} - Google Authorization</title>
            <script>
                window.onload = function() {{
                    if (window.opener) {{
                        window.opener.postMessage(
                            JSON.stringify({json.dumps(context)}),
                            "*"
                        );
                        window.close();
                    }} else {{
                        document.getElementById('message').style.display = 'block';
                    }}
                }};
            </script>
        </head>
        <body>
            <div id="message" style="display:none; text-align:center; margin-top:50px;">
                <h3>{'Success' if success else 'Error'}</h3>
                <p>{context['message']}</p>
                <p>You can close this window now.</p>
            </div>
        </body>
        </html>
        """
        
        return HttpResponse(html)


class TwitterPostView(views.APIView):
    """
    Post content to Twitter accounts
    """
    permission_classes = [IsAuthenticated]
    
    def post(self, request, format=None):
        """Create a post on Twitter"""
        # Get post data
        post_data = request.data
        text = post_data.get('text')
        media_ids = post_data.get('media_ids', [])
        scheduled_time = post_data.get('scheduled_time')  # Optional, for scheduling
        account_id = post_data.get('account_id')
        
        # Validate essential data
        if not text:
            return Response(
                {'error': 'Text content is required for Twitter posts'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Get the user's Twitter account
        try:
            if account_id:
                account = UserSocialAccount.objects.get(
                    id=account_id,
                    user=request.user,
                    platform__name='twitter',
                    status='active'
                )
            else:
                # Get primary Twitter account if account_id not specified
                account = UserSocialAccount.objects.get(
                    user=request.user,
                    platform__name='twitter',
                    is_primary=True,
                    status='active'
                )
        except UserSocialAccount.DoesNotExist:
            return Response(
                {'error': 'No active Twitter account found'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # Refresh token if needed
        if account.is_expired:
            if not refresh_token_if_needed(account):
                return Response(
                    {'error': 'Twitter token expired and could not be refreshed'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
        
        # If scheduled_time is provided, create a scheduled post
        if scheduled_time:
            try:
                # Convert to datetime if it's a string
                if isinstance(scheduled_time, str):
                    scheduled_time = datetime.fromisoformat(scheduled_time.replace('Z', '+00:00'))
                
                # Store in DB for later processing (implementation depends on your schedule processing system)
                # For example:
                # ScheduledPost.objects.create(
                #     user=request.user,
                #     account=account,
                #     content=text,
                #     media_ids=media_ids,
                #     scheduled_time=scheduled_time
                # )
                
                return Response({
                    'success': True,
                    'message': f'Post scheduled for {scheduled_time.isoformat()}'
                })
            except Exception as e:
                logger.error(f"Error scheduling Twitter post: {str(e)}")
                return Response(
                    {'error': f'Failed to schedule Twitter post: {str(e)}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
        
        # Post immediately if no scheduled_time
        try:
            # Prepare API call to Twitter
            api_url = "https://api.twitter.com/2/tweets"
            headers = {
                'Authorization': f'Bearer {account.access_token}',
                'Content-Type': 'application/json'
            }
            
            payload = {
                'text': text
            }
            
            # Include media if provided
            if media_ids:
                payload['media'] = {
                    'media_ids': media_ids
                }
            
            # Make the API call
            response = requests.post(api_url, headers=headers, json=payload)
            
            if response.status_code != 201:
                return Response(
                    {'error': f'Twitter API error: {response.text}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Parse response to get tweet ID
            tweet_data = response.json()
            
            # Update account usage timestamp
            account.last_used_at = timezone.now()
            account.save()
            
            return Response({
                'success': True,
                'tweet_id': tweet_data.get('data', {}).get('id'),
                'text': text
            })
            
        except Exception as e:
            logger.error(f"Error posting to Twitter: {str(e)}")
            return Response(
                {'error': f'Failed to post to Twitter: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class TwitterAnalyticsView(views.APIView):
    """
    Retrieve analytics for Twitter accounts
    """
    permission_classes = [IsAuthenticated]
    
    def get(self, request, format=None):
        """Get analytics for a Twitter account"""
        account_id = request.query_params.get('account_id')
        period = request.query_params.get('period', '30d')  # Default to 30 days
        
        # Validate account_id
        if not account_id:
            return Response(
                {'error': 'account_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
            
        # Get the account
        try:
            account = UserSocialAccount.objects.get(
                id=account_id,
                user=request.user,
                platform__name='twitter',
                status='active'
            )
        except UserSocialAccount.DoesNotExist:
            return Response(
                {'error': 'Twitter account not found or not active'},
                status=status.HTTP_404_NOT_FOUND
            )
            
        # Refresh token if needed
        if account.is_expired:
            if not refresh_token_if_needed(account):
                return Response(
                    {'error': 'Twitter token expired and could not be refreshed'},
                    status=status.HTTP_401_UNAUTHORIZED
                )
                
        # Calculate date range based on period
        end_date = timezone.now()
        if period == '7d':
            start_date = end_date - timedelta(days=7)
        elif period == '14d':
            start_date = end_date - timedelta(days=14)
        elif period == '30d':
            start_date = end_date - timedelta(days=30)
        elif period == '90d':
            start_date = end_date - timedelta(days=90)
        else:
            # Default to 30 days if invalid period
            start_date = end_date - timedelta(days=30)
            
        # Format dates for Twitter API
        start_date_str = start_date.strftime('%Y-%m-%d')
        end_date_str = end_date.strftime('%Y-%m-%d')
        
        try:
            # Get Twitter user ID from account
            user_id = account.account_id
            
            # Make API call to get user metrics
            headers = {
                'Authorization': f'Bearer {account.access_token}',
                'Content-Type': 'application/json'
            }
            
            # Getting user profile with public metrics
            profile_url = f"https://api.twitter.com/2/users/{user_id}?user.fields=public_metrics,profile_image_url,verified,description"
            profile_response = requests.get(profile_url, headers=headers)
            
            if profile_response.status_code != 200:
                return Response(
                    {'error': f'Twitter API error: {profile_response.text}'},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            profile_data = profile_response.json().get('data', {})
            public_metrics = profile_data.get('public_metrics', {})
            
            # Get recent tweets to analyze engagement
            tweets_url = f"https://api.twitter.com/2/users/{user_id}/tweets?max_results=100&tweet.fields=public_metrics,created_at"
            tweets_response = requests.get(tweets_url, headers=headers)
            
            tweet_analytics = {
                'total_tweets': 0,
                'total_likes': 0,
                'total_retweets': 0,
                'total_replies': 0,
                'avg_engagement_rate': 0,
                'period': {
                    'start': start_date_str,
                    'end': end_date_str
                }
            }
            
            if tweets_response.status_code == 200:
                tweets_data = tweets_response.json()
                tweets = tweets_data.get('data', [])
                
                if tweets:
                    # Filter tweets by date range and calculate metrics
                    filtered_tweets = [
                        t for t in tweets 
                        if start_date_str <= t.get('created_at', '')[:10] <= end_date_str
                    ]
                    
                    tweet_analytics['total_tweets'] = len(filtered_tweets)
                    
                    # Calculate engagement metrics
                    if filtered_tweets:
                        total_likes = sum(t.get('public_metrics', {}).get('like_count', 0) for t in filtered_tweets)
                        total_retweets = sum(t.get('public_metrics', {}).get('retweet_count', 0) for t in filtered_tweets)
                        total_replies = sum(t.get('public_metrics', {}).get('reply_count', 0) for t in filtered_tweets)
                        
                        tweet_analytics['total_likes'] = total_likes
                        tweet_analytics['total_retweets'] = total_retweets
                        tweet_analytics['total_replies'] = total_replies
                        
                        # Calculate average engagement rate
                        followers = public_metrics.get('followers_count', 1)  # Avoid division by zero
                        if followers > 0:
                            total_engagement = total_likes + total_retweets + total_replies
                            avg_engagement = (total_engagement / len(filtered_tweets)) / followers * 100
                            tweet_analytics['avg_engagement_rate'] = round(avg_engagement, 2)
            
            # Combine everything into a comprehensive analytics response
            result = {
                'account_info': {
                    'id': account.id,
                    'username': profile_data.get('username'),
                    'name': profile_data.get('name'),
                    'profile_image_url': profile_data.get('profile_image_url'),
                    'verified': profile_data.get('verified', False),
                    'description': profile_data.get('description')
                },
                'followers': public_metrics.get('followers_count', 0),
                'following': public_metrics.get('following_count', 0),
                'tweet_count': public_metrics.get('tweet_count', 0),
                'tweet_analytics': tweet_analytics,
                'period': period
            }
            
            return Response(result)
            
        except Exception as e:
            logger.error(f"Error fetching Twitter analytics: {str(e)}")
            return Response(
                {'error': f'Failed to fetch Twitter analytics: {str(e)}'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
