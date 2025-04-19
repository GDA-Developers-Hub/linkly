from django.conf import settings
import requests
import hashlib
import hmac
import time
from rest_framework import status
from rest_framework.exceptions import ValidationError
import tweepy
from django.utils import timezone

class SocialConnectionError(Exception):
    pass

def exchange_google_code(code, redirect_uri=None):
    """Exchange Google auth code for tokens"""
    try:
        response = requests.post(
            'https://oauth2.googleapis.com/token',
            data={
                'client_id': settings.GOOGLE_CLIENT_ID,
                'client_secret': settings.GOOGLE_CLIENT_SECRET,
                'code': code,
                'redirect_uri': redirect_uri or settings.GOOGLE_REDIRECT_URI,
                'grant_type': 'authorization_code'
            }
        )
        if response.status_code != 200:
            raise SocialConnectionError('Failed to exchange Google auth code')
        return response.json()
    except Exception as e:
        raise SocialConnectionError(f'Google OAuth error: {str(e)}')

def exchange_facebook_code(code, redirect_uri=None):
    """Exchange Facebook auth code for tokens"""
    try:
        response = requests.get(
            'https://graph.facebook.com/v18.0/oauth/access_token',
            params={
                'client_id': settings.FACEBOOK_CLIENT_ID,
                'client_secret': settings.FACEBOOK_CLIENT_SECRET,
                'code': code,
                'redirect_uri': redirect_uri or settings.FACEBOOK_REDIRECT_URI
            }
        )
        if response.status_code != 200:
            raise SocialConnectionError('Failed to exchange Facebook auth code')
        return response.json()
    except Exception as e:
        raise SocialConnectionError(f'Facebook OAuth error: {str(e)}')

def exchange_linkedin_code(code, redirect_uri=None):
    """Exchange LinkedIn auth code for tokens"""
    try:
        response = requests.post(
            'https://www.linkedin.com/oauth/v2/accessToken',
            data={
                'grant_type': 'authorization_code',
                'code': code,
                'client_id': settings.LINKEDIN_CLIENT_ID,
                'client_secret': settings.LINKEDIN_CLIENT_SECRET,
                'redirect_uri': redirect_uri or settings.LINKEDIN_REDIRECT_URI
            }
        )
        if response.status_code != 200:
            raise SocialConnectionError('Failed to exchange LinkedIn auth code')
        return response.json()
    except Exception as e:
        raise SocialConnectionError(f'LinkedIn OAuth error: {str(e)}')

def exchange_twitter_code(code, redirect_uri=None):
    """Exchange Twitter auth code for tokens"""
    try:
        response = requests.post(
            'https://api.twitter.com/2/oauth2/token',
            data={
                'code': code,
                'grant_type': 'authorization_code',
                'client_id': settings.TWITTER_CLIENT_ID,
                'client_secret': settings.TWITTER_CLIENT_SECRET,
                'redirect_uri': redirect_uri or settings.TWITTER_REDIRECT_URI,
                'code_verifier': 'challenge'
            }
        )
        if response.status_code != 200:
            raise SocialConnectionError('Failed to exchange Twitter auth code')
        return response.json()
    except Exception as e:
        raise SocialConnectionError(f'Twitter OAuth error: {str(e)}')

def exchange_instagram_code(code, redirect_uri=None):
    """Exchange Instagram auth code for tokens"""
    try:
        response = requests.post(
            'https://api.instagram.com/oauth/access_token',
            data={
                'client_id': settings.INSTAGRAM_CLIENT_ID,
                'client_secret': settings.INSTAGRAM_CLIENT_SECRET,
                'grant_type': 'authorization_code',
                'redirect_uri': redirect_uri or settings.INSTAGRAM_REDIRECT_URI,
                'code': code
            }
        )
        if response.status_code != 200:
            raise SocialConnectionError('Failed to exchange Instagram auth code')
        return response.json()
    except Exception as e:
        raise SocialConnectionError(f'Instagram OAuth error: {str(e)}')

def exchange_tiktok_code(code, redirect_uri=None):
    """Exchange TikTok auth code for tokens"""
    try:
        response = requests.post(
            'https://open-api.tiktok.com/oauth/access_token/',
            params={
                'client_key': settings.TIKTOK_CLIENT_KEY,
                'client_secret': settings.TIKTOK_CLIENT_SECRET,
                'code': code,
                'grant_type': 'authorization_code'
            }
        )
        if response.status_code != 200:
            raise SocialConnectionError('Failed to exchange TikTok auth code')
        return response.json()
    except Exception as e:
        raise SocialConnectionError(f'TikTok OAuth error: {str(e)}')

def verify_telegram_data(auth_data):
    """
    Verify Telegram login widget data
    https://core.telegram.org/widgets/login#checking-authorization
    """
    try:
        # Get the hash and remove it from the data
        received_hash = auth_data.pop('hash', '')
        auth_string = []
        
        # Sort the remaining fields alphabetically
        for key in sorted(auth_data.keys()):
            if auth_data[key] is not None:
                auth_string.append(f'{key}={auth_data[key]}')
        
        # Join the sorted fields
        auth_string = '\n'.join(auth_string)
        
        # Create a secret key using SHA256
        secret_key = hashlib.sha256(settings.TELEGRAM_BOT_TOKEN.encode()).digest()
        
        # Calculate the hash using HMAC-SHA256
        computed_hash = hmac.new(
            secret_key,
            auth_string.encode(),
            hashlib.sha256
        ).hexdigest()
        
        # Verify the hash
        if computed_hash != received_hash:
            raise SocialConnectionError('Invalid Telegram authentication data')
        
        # Check if the auth data is not expired (default 1 day)
        auth_date = int(auth_data.get('auth_date', 0))
        if time.time() - auth_date > 86400:
            raise SocialConnectionError('Telegram authentication data has expired')
            
        return True
        
    except Exception as e:
        raise SocialConnectionError(f'Telegram verification error: {str(e)}')

def connect_social_account(user, platform, auth_data, business=False):
    """Connect a social media account to a user"""
    platform = platform.lower()
    
    try:
        if platform == 'google':
            tokens = exchange_google_code(auth_data.get('code'), auth_data.get('redirect_uri'))
            user.google_access_token = tokens.get('access_token')
            user.google_refresh_token = tokens.get('refresh_token')
            if business:
                user.google_business_connected = True
        
        elif platform == 'facebook':
            tokens = exchange_facebook_code(auth_data.get('code'), auth_data.get('redirect_uri'))
            user.facebook_access_token = tokens.get('access_token')
            if business:
                user.facebook_business_connected = True
        
        elif platform == 'linkedin':
            tokens = exchange_linkedin_code(auth_data.get('code'), auth_data.get('redirect_uri'))
            user.linkedin_access_token = tokens.get('access_token')
            if business:
                user.linkedin_business_connected = True
        
        elif platform == 'twitter':
            tokens = exchange_twitter_code(auth_data.get('code'), auth_data.get('redirect_uri'))
            user.twitter_access_token = tokens.get('access_token')
            if business:
                user.twitter_business_connected = True
        
        elif platform == 'instagram':
            if business:
                # Instagram Business uses Facebook authentication
                tokens = exchange_facebook_code(auth_data.get('code'), auth_data.get('redirect_uri'))
                user.instagram_business_access_token = tokens.get('access_token')
                user.instagram_business_connected = True
            else:
                tokens = exchange_instagram_code(auth_data.get('code'), auth_data.get('redirect_uri'))
                user.instagram_access_token = tokens.get('access_token')
        
        elif platform == 'tiktok':
            tokens = exchange_tiktok_code(auth_data.get('code'), auth_data.get('redirect_uri'))
            user.tiktok_access_token = tokens.get('access_token')
            if business:
                user.tiktok_business_connected = True
        
        elif platform == 'telegram':
            if verify_telegram_data(auth_data):
                user.telegram_id = auth_data.get('id')
                if business:
                    user.telegram_business_connected = True
        
        else:
            raise ValidationError({'platform': ['Invalid platform specified.']})
        
        user.save()
        return user
        
    except SocialConnectionError as e:
        raise ValidationError({'detail': str(e)})
    except Exception as e:
        raise ValidationError({'detail': f'Failed to connect {platform} account: {str(e)}'})

def fetch_google_user_data(access_token):
    """Fetch Google user profile data"""
    try:
        response = requests.get(
            'https://www.googleapis.com/oauth2/v3/userinfo',
            headers={'Authorization': f'Bearer {access_token}'}
        )
        if response.status_code != 200:
            raise SocialConnectionError('Failed to fetch Google user data')
        return response.json()
    except Exception as e:
        raise SocialConnectionError(f'Google API error: {str(e)}')

def fetch_facebook_user_data(access_token):
    """Fetch Facebook user profile and page data"""
    try:
        # Get user profile
        profile = requests.get(
            'https://graph.facebook.com/me',
            params={
                'fields': 'id,name,email,picture',
                'access_token': access_token
            }
        ).json()
        
        # Get user's pages
        pages = requests.get(
            'https://graph.facebook.com/me/accounts',
            params={'access_token': access_token}
        ).json()
        
        return {
            'profile': profile,
            'pages': pages.get('data', [])
        }
    except Exception as e:
        raise SocialConnectionError(f'Facebook API error: {str(e)}')

def fetch_linkedin_user_data(access_token):
    """Fetch LinkedIn user profile and company data"""
    try:
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Get basic profile
        profile = requests.get(
            'https://api.linkedin.com/v2/me',
            headers=headers
        ).json()
        
        # Get email address
        email = requests.get(
            'https://api.linkedin.com/v2/emailAddress?q=members&projection=(elements*(handle~))',
            headers=headers
        ).json()
        
        # Get company data if available
        companies = requests.get(
            'https://api.linkedin.com/v2/organizationalEntityAcls?q=roleAssignee',
            headers=headers
        ).json()
        
        return {
            'profile': profile,
            'email': email.get('elements', [{}])[0].get('handle~', {}).get('emailAddress'),
            'companies': companies.get('elements', [])
        }
    except Exception as e:
        raise SocialConnectionError(f'LinkedIn API error: {str(e)}')

def fetch_twitter_user_data(access_token, access_token_secret):
    """Fetch Twitter user profile data"""
    try:
        auth = tweepy.OAuthHandler(
            settings.TWITTER_API_KEY,
            settings.TWITTER_API_SECRET
        )
        auth.set_access_token(access_token, access_token_secret)
        api = tweepy.API(auth)
        
        # Get user profile
        user = api.verify_credentials()
        
        return {
            'id': user.id_str,
            'username': user.screen_name,
            'name': user.name,
            'profile_image': user.profile_image_url_https,
            'followers_count': user.followers_count,
            'friends_count': user.friends_count,
            'statuses_count': user.statuses_count
        }
    except Exception as e:
        raise SocialConnectionError(f'Twitter API error: {str(e)}')

def fetch_instagram_user_data(access_token):
    """Fetch Instagram user profile data"""
    try:
        # Get user profile
        profile = requests.get(
            'https://graph.instagram.com/me',
            params={
                'fields': 'id,username,account_type,media_count',
                'access_token': access_token
            }
        ).json()
        
        # Get user media
        media = requests.get(
            'https://graph.instagram.com/me/media',
            params={
                'fields': 'id,caption,media_type,media_url,thumbnail_url,permalink',
                'access_token': access_token
            }
        ).json()
        
        return {
            'profile': profile,
            'recent_media': media.get('data', [])
        }
    except Exception as e:
        raise SocialConnectionError(f'Instagram API error: {str(e)}')

def fetch_tiktok_user_data(access_token, open_id):
    """Fetch TikTok user profile data"""
    try:
        # Get user info
        response = requests.get(
            'https://open-api.tiktok.com/user/info/',
            params={
                'access_token': access_token,
                'open_id': open_id,
                'fields': ['open_id', 'union_id', 'avatar_url', 'display_name', 
                          'bio_description', 'profile_deep_link', 'follower_count', 
                          'following_count', 'likes_count', 'video_count']
            }
        )
        
        if response.status_code != 200:
            raise SocialConnectionError('Failed to fetch TikTok user data')
            
        return response.json().get('data', {})
    except Exception as e:
        raise SocialConnectionError(f'TikTok API error: {str(e)}')

def fetch_telegram_channel_data(chat_id):
    """Fetch Telegram channel data"""
    try:
        bot_token = settings.TELEGRAM_BOT_TOKEN
        
        # Get chat info
        chat_info = requests.get(
            f'https://api.telegram.org/bot{bot_token}/getChat',
            params={'chat_id': chat_id}
        ).json()
        
        if not chat_info.get('ok'):
            raise SocialConnectionError('Failed to fetch Telegram channel info')
        
        # Get member count
        member_count = requests.get(
            f'https://api.telegram.org/bot{bot_token}/getChatMemberCount',
            params={'chat_id': chat_id}
        ).json()
        
        return {
            'chat': chat_info.get('result', {}),
            'member_count': member_count.get('result', 0)
        }
    except Exception as e:
        raise SocialConnectionError(f'Telegram API error: {str(e)}')

def fetch_youtube_channel_data(access_token, channel_id):
    """Fetch YouTube channel data"""
    try:
        headers = {'Authorization': f'Bearer {access_token}'}
        
        # Get channel details
        channel_response = requests.get(
            'https://youtube.googleapis.com/youtube/v3/channels',
            params={
                'part': 'snippet,statistics,brandingSettings',
                'id': channel_id
            },
            headers=headers
        ).json()
        
        if 'error' in channel_response:
            raise SocialConnectionError('Failed to fetch YouTube channel data')
            
        channel = channel_response.get('items', [{}])[0]
        
        return {
            'snippet': channel.get('snippet', {}),
            'statistics': channel.get('statistics', {}),
            'branding': channel.get('brandingSettings', {})
        }
    except Exception as e:
        raise SocialConnectionError(f'YouTube API error: {str(e)}')

def update_user_social_data(user, platform, data):
    """Update user's social media data"""
    try:
        if platform == 'google':
            user.email = data.get('email')
            user.first_name = data.get('given_name', '')
            user.last_name = data.get('family_name', '')
            user.profile_picture = data.get('picture')
            
        elif platform == 'facebook':
            profile = data.get('profile', {})
            user.facebook_page = f"https://facebook.com/{profile.get('id')}"
            if data.get('pages'):
                page = data['pages'][0]  # Get first page
                user.facebook_page_id = page.get('id')
                user.facebook_page_name = page.get('name')
                user.facebook_page_token = page.get('access_token')
                
        elif platform == 'linkedin':
            profile = data.get('profile', {})
            user.linkedin_profile = f"https://linkedin.com/in/{profile.get('vanityName', '')}"
            if data.get('companies'):
                company = data['companies'][0]  # Get first company
                user.linkedin_company_id = company.get('organizationalTarget')
                user.has_linkedin_company = True
                
        elif platform == 'twitter':
            user.twitter_handle = data.get('username')
            user.twitter_profile_url = f"https://twitter.com/{data.get('username')}"
            user.twitter_followers = data.get('followers_count', 0)
            
        elif platform == 'instagram':
            profile = data.get('profile', {})
            user.instagram_handle = profile.get('username')
            user.instagram_profile_url = f"https://instagram.com/{profile.get('username')}"
            if profile.get('account_type') == 'BUSINESS':
                user.has_instagram_business = True
                
        elif platform == 'tiktok':
            user.tiktok_handle = data.get('display_name')
            user.tiktok_profile_url = data.get('profile_deep_link')
            user.tiktok_followers = data.get('follower_count', 0)
            
        elif platform == 'telegram':
            chat = data.get('chat', {})
            user.telegram_channel_name = chat.get('title')
            user.telegram_subscribers = data.get('member_count', 0)
            
        elif platform == 'youtube':
            snippet = data.get('snippet', {})
            stats = data.get('statistics', {})
            user.youtube_channel_title = snippet.get('title')
            user.youtube_channel = f"https://youtube.com/channel/{snippet.get('channelId')}"
            user.youtube_subscribers = int(stats.get('subscriberCount', 0))
            
        user.metrics_last_updated = timezone.now()
        user.update_last_sync(platform)
        user.save()
        
    except Exception as e:
        raise SocialConnectionError(f'Failed to update user data: {str(e)}')

def connect_google_account(user, auth_code, redirect_uri=None, business=False):
    """Connect Google account to user"""
    try:
        # Exchange auth code for tokens
        tokens = exchange_google_code(auth_code, redirect_uri)
        if not tokens:
            raise SocialConnectionError('Failed to exchange Google auth code')

        # Fetch user data
        user_data = fetch_google_user_data(tokens['access_token'])
        if not user_data:
            raise SocialConnectionError('Failed to fetch Google user data')

        # Update user's Google tokens
        user.google_access_token = tokens.get('access_token')
        user.google_refresh_token = tokens.get('refresh_token')
        user.google_id = user_data.get('sub')
        user.update_social_token('google', tokens['access_token'], tokens.get('expires_in', 3600))

        if business:
            user.google_business_connected = True

        # Update user profile data
        update_user_social_data(user, 'google', user_data)

        return {
            'success': True,
            'user_id': user.google_id,
            'email': user_data.get('email')
        }

    except Exception as e:
        raise SocialConnectionError(f'Failed to connect Google account: {str(e)}')

def connect_facebook_account(user, auth_code, redirect_uri=None, business=False):
    """Connect Facebook account to user"""
    try:
        # Exchange auth code for tokens
        tokens = exchange_facebook_code(auth_code, redirect_uri)
        if not tokens:
            raise SocialConnectionError('Failed to exchange Facebook auth code')

        # Fetch user data
        user_data = fetch_facebook_user_data(tokens['access_token'])
        if not user_data:
            raise SocialConnectionError('Failed to fetch Facebook user data')

        # Update user's Facebook tokens
        user.facebook_access_token = tokens['access_token']
        user.facebook_id = user_data['profile'].get('id')
        user.update_social_token('facebook', tokens['access_token'])

        if business and user_data.get('pages'):
            user.has_facebook_business = True

        # Update user profile data
        update_user_social_data(user, 'facebook', user_data)

        return {
            'success': True,
            'user_id': user.facebook_id,
            'pages': user_data.get('pages', [])
        }

    except Exception as e:
        raise SocialConnectionError(f'Failed to connect Facebook account: {str(e)}')

def connect_linkedin_account(user, auth_code, redirect_uri=None, business=False):
    """Connect LinkedIn account to user"""
    try:
        # Exchange auth code for tokens
        tokens = exchange_linkedin_code(auth_code, redirect_uri)
        if not tokens:
            raise SocialConnectionError('Failed to exchange LinkedIn auth code')

        # Fetch user data
        user_data = fetch_linkedin_user_data(tokens['access_token'])
        if not user_data:
            raise SocialConnectionError('Failed to fetch LinkedIn user data')

        # Update user's LinkedIn tokens
        user.linkedin_access_token = tokens['access_token']
        user.linkedin_id = user_data['profile'].get('id')
        user.update_social_token('linkedin', tokens['access_token'])

        if business and user_data.get('companies'):
            user.has_linkedin_company = True

        # Update user profile data
        update_user_social_data(user, 'linkedin', user_data)

        return {
            'success': True,
            'user_id': user.linkedin_id,
            'companies': user_data.get('companies', [])
        }

    except Exception as e:
        raise SocialConnectionError(f'Failed to connect LinkedIn account: {str(e)}')

def connect_twitter_account(user, auth_code, redirect_uri=None, business=False):
    """Connect Twitter account to user"""
    try:
        # Exchange auth code for tokens
        tokens = exchange_twitter_code(auth_code, redirect_uri)
        if not tokens:
            raise SocialConnectionError('Failed to exchange Twitter auth code')

        # Fetch user data
        user_data = fetch_twitter_user_data(
            tokens['access_token'],
            tokens.get('access_token_secret', '')
        )
        if not user_data:
            raise SocialConnectionError('Failed to fetch Twitter user data')

        # Update user's Twitter tokens
        user.twitter_access_token = tokens['access_token']
        user.twitter_access_token_secret = tokens.get('access_token_secret')
        user.twitter_id = user_data['id']
        user.update_social_token('twitter', tokens['access_token'])

        if business:
            user.has_twitter_business = True

        # Update user profile data
        update_user_social_data(user, 'twitter', user_data)

        return {
            'success': True,
            'user_id': user.twitter_id,
            'username': user_data['username']
        }

    except Exception as e:
        raise SocialConnectionError(f'Failed to connect Twitter account: {str(e)}')

def connect_instagram_account(user, auth_code, redirect_uri=None, business=False):
    """Connect Instagram account to user"""
    try:
        if business:
            # Instagram Business uses Facebook authentication
            tokens = exchange_facebook_code(auth_code, redirect_uri)
            if not tokens:
                raise SocialConnectionError('Failed to exchange Facebook auth code for Instagram Business')
        else:
            tokens = exchange_instagram_code(auth_code, redirect_uri)
            if not tokens:
                raise SocialConnectionError('Failed to exchange Instagram auth code')

        # Fetch user data
        user_data = fetch_instagram_user_data(tokens['access_token'])
        if not user_data:
            raise SocialConnectionError('Failed to fetch Instagram user data')

        # Update user's Instagram tokens
        if business:
            user.instagram_business_token = tokens['access_token']
            user.instagram_business_id = user_data['profile'].get('id')
            user.has_instagram_business = True
        else:
            user.instagram_access_token = tokens['access_token']
            user.instagram_id = user_data['profile'].get('id')

        user.update_social_token('instagram', tokens['access_token'])

        # Update user profile data
        update_user_social_data(user, 'instagram', user_data)

        return {
            'success': True,
            'user_id': user.instagram_business_id if business else user.instagram_id,
            'username': user_data['profile'].get('username')
        }

    except Exception as e:
        raise SocialConnectionError(f'Failed to connect Instagram account: {str(e)}')

def connect_tiktok_account(user, auth_code, redirect_uri=None, business=False):
    """Connect TikTok account to user"""
    try:
        # Exchange auth code for tokens
        tokens = exchange_tiktok_code(auth_code, redirect_uri)
        if not tokens:
            raise SocialConnectionError('Failed to exchange TikTok auth code')

        # Fetch user data
        user_data = fetch_tiktok_user_data(
            tokens['access_token'],
            tokens.get('open_id')
        )
        if not user_data:
            raise SocialConnectionError('Failed to fetch TikTok user data')

        # Update user's TikTok tokens
        user.tiktok_access_token = tokens['access_token']
        user.tiktok_id = tokens.get('open_id')
        user.update_social_token('tiktok', tokens['access_token'])

        if business:
            user.has_tiktok_business = True

        # Update user profile data
        update_user_social_data(user, 'tiktok', user_data)

        return {
            'success': True,
            'user_id': user.tiktok_id,
            'username': user_data.get('display_name')
        }

    except Exception as e:
        raise SocialConnectionError(f'Failed to connect TikTok account: {str(e)}')

def connect_telegram_account(user, auth_data, redirect_uri=None, business=False):
    """Connect Telegram account to user"""
    try:
        # Verify Telegram authentication data
        if not verify_telegram_data(auth_data):
            raise SocialConnectionError('Invalid Telegram authentication data')

        # Get user's Telegram ID
        telegram_id = auth_data.get('id')
        if not telegram_id:
            raise SocialConnectionError('Telegram ID not found in auth data')

        # Fetch channel data if it's a business account
        if business:
            channel_data = fetch_telegram_channel_data(telegram_id)
            if not channel_data:
                raise SocialConnectionError('Failed to fetch Telegram channel data')

        # Update user's Telegram info
        user.telegram_id = telegram_id
        user.telegram_username = auth_data.get('username')
        user.telegram_chat_id = telegram_id

        if business:
            user.has_telegram_channel = True
            update_user_social_data(user, 'telegram', channel_data)

        user.update_last_sync('telegram')
        user.save()

        return {
            'success': True,
            'user_id': user.telegram_id,
            'username': user.telegram_username
        }

    except Exception as e:
        raise SocialConnectionError(f'Failed to connect Telegram account: {str(e)}') 