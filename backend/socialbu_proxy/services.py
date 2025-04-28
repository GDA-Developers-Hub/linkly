import requests
import json
import logging
import string
import random
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import SocialBuToken

User = get_user_model()
logger = logging.getLogger(__name__)

def generate_secure_password(length=16):
    """Generate a secure random password"""
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password

class SocialBuService:
    """
    Service to interact with SocialBu API
    """
    BASE_URL = settings.SOCIALBU_API_URL

    def __init__(self, token=None):
        self.token = token
        
    def get_headers(self):
        headers = {
            'Content-Type': 'application/json',
        }
        
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
            
        return headers
    
    def make_request(self, endpoint, method='GET', data=None, files=None):
        """
        Make a request to SocialBu API
        """
        # Strip any leading slashes
        endpoint = endpoint.lstrip('/')
        logger.info(f"Endpoint after stripping leading slashes: '{endpoint}'")
        
        # Use the BASE_URL directly without any additional processing
        # The frontend will provide the complete base URL including any api/v1
        url = f"{self.BASE_URL}/api/v1/{endpoint}"
        logger.info(f"Constructed URL: {url}")
            
        headers = self.get_headers()
        logger.info(f"Request headers: {headers}")
        
        # Use the existing logger instead of redefining it
        logger.info(f"Making {method} request to SocialBu API: {url}")
        if data:
            logger.info(f"Request data: {data}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers)
            elif method == 'POST':
                if files:
                    # For file uploads, don't use JSON
                    headers.pop('Content-Type', None)
                    response = requests.post(url, headers=headers, data=data, files=files)
                else:
                    response = requests.post(url, headers=headers, json=data)
            elif method == 'PUT':
                response = requests.put(url, headers=headers, json=data)
            elif method == 'DELETE':
                response = requests.delete(url, headers=headers)
            else:
                raise ValueError(f"Unsupported method: {method}")
            
            logger.info(f"SocialBu API Response status: {response.status_code}")
            
            # Log the raw response for debugging
            try:
                logger.debug(f"Raw response: {response.text[:1000]}")  # Log first 1000 chars to avoid huge logs
            except Exception as e:
                logger.debug(f"Could not log raw response: {str(e)}")
                
            response.raise_for_status()
            
            if response.status_code == 204:  # No content
                logger.info("SocialBu API returned no content")
                return None
            
            result = response.json()
            logger.info(f"SocialBu API Response data: {result}")
            return result
        except requests.exceptions.ConnectionError as e:
            logger.error(f"CONNECTION ERROR: Could not connect to SocialBu API: {url}")
            logger.error(f"Connection error details: {str(e)}")
            raise SocialBuAPIError(f"Could not connect to SocialBu API: {str(e)}", 503)
        except requests.exceptions.Timeout as e:
            logger.error(f"TIMEOUT: SocialBu API request timed out: {url}")
            logger.error(f"Timeout error details: {str(e)}")
            raise SocialBuAPIError(f"SocialBu API request timed out: {str(e)}", 504)
        except requests.exceptions.RequestException as e:
            logger.error(f"API ERROR: SocialBu API error: {str(e)}")
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_data = e.response.json()
                    error_message = error_data.get('message', str(e))
                    logger.error(f"API error response: {error_data}")
                except ValueError:
                    error_message = str(e)
                    
                status_code = e.response.status_code
            else:
                error_message = str(e)
                status_code = 500
                
            raise SocialBuAPIError(error_message, status_code)
    
    # User Management
    def register(self, name, email, password):
        """Register a new user with SocialBu"""
        logger.info(f"Attempting to register user with SocialBu: {email}")
        
        # Make a request to the SocialBu registration endpoint
        result = self.make_request('auth/register', 'POST', {
            'name': name,
            'email': email,
            'password': password
        })
        
        logger.info(f"SocialBu registration successful: {email}")
        return result
    
    # Authentication
    def authenticate(self, email, password, base_url=None):
        """Authenticate with SocialBu API"""
        logger.info(f"Attempting to authenticate with SocialBu API: {email}")
        
        # Use exactly the format specified in the API documentation
        payload = {
            "email": email,
            "password": password
        }
        
        # Save original BASE_URL
        original_base_url = self.BASE_URL
        
        try:
            # Temporarily override BASE_URL if provided
            if base_url:
                logger.info(f"Using custom base URL: {base_url}")
                self.BASE_URL = base_url
            else:
                logger.info(f"Using default base URL: {self.BASE_URL}")
                
            # Log the endpoint we're going to call
            endpoint = 'auth/get_token'
            url = f"{self.BASE_URL}/{endpoint}"
            logger.info(f"Authentication endpoint: {endpoint}")
            logger.info(f"Full authentication URL: {url}")
                
            # Call the endpoint
            result = self.make_request('auth/get_token', 'POST', payload)
            
            logger.info(f"Authentication result: {result}")
            
            # Map the response fields to our expected format
            return {
                'token': result.get('authToken') or result.get('token') or result.get('access_token'),
                'user_id': result.get('id') or result.get('user_id'),
                'name': result.get('name'),
                'email': result.get('email'),
                'verified': result.get('verified', False)
            }
        except Exception as e:
            logger.error(f"Authentication exception: {str(e)}")
            raise
        finally:
            # Restore original BASE_URL
            logger.info(f"Restoring original base URL: {original_base_url}")
            self.BASE_URL = original_base_url
    
    def logout(self):
        """Logout from SocialBu API"""
        if not self.token:
            logger.info("No token to logout with")
            return {"success": False, "message": "No token provided"}
        
        # Call the logout endpoint
        try:
            return self.make_request('auth/logout', 'POST')
        except SocialBuAPIError:
            # Even if the API call fails, we consider it a success 
            # since we're deleting the token from our db anyway
            return {"success": True}
    
    # Social Platform Connection
    def get_connection_url(self, provider, postback_url, account_id=None):
        """Get URL for connecting a social platform"""
        logger.info(f"Getting connection URL for provider: {provider}, postback: {postback_url}")
        
        # Prepare the data in the format SocialBu API expects
        data = {
            'provider': provider,
            'postback_url': postback_url
        }
        
        if account_id:
            data['account_id'] = account_id
            
        # Make the API call to the accounts endpoint
        return self.make_request('accounts', 'POST', data)
    
    # Posts
    def get_posts(self, limit=None, status=None):
        """Get posts from SocialBu API"""
        logger.info(f"Fetching posts from SocialBu API with limit={limit}, status={status}")
        
        endpoint = 'posts'
        params = []
        
        if limit:
            params.append(f'limit={limit}')
        
        if status:
            params.append(f'status={status}')
            
        if params:
            endpoint += f"?{'&'.join(params)}"
        
        logger.info(f"Calling SocialBu API endpoint: {endpoint}")
        result = self.make_request(endpoint)
        
        # Handle both expected response formats
        # New format: { "items": [...], "currentPage": n, "lastPage": n, "nextPage": n, "total": n }
        # Old format: [...] (array of posts)
        if isinstance(result, dict) and 'items' in result:
            logger.info(f"Received paginated posts response. Total posts: {result.get('total', 0)}")
            return result
        else:
            # If we got a simple array, wrap it in the expected format
            logger.info(f"Received array posts response. Total posts: {len(result) if result else 0}")
            return {
                "items": result or [],
                "currentPage": 1,
                "lastPage": 1,
                "nextPage": None,
                "total": len(result) if result else 0
            }
    
    def create_post(self, data):
        """Create a post in SocialBu API"""
        logger.info(f"Creating post with data: {json.dumps(data, indent=2)}")
        
        # Make sure we're using the correct endpoint as per the requirements
        endpoint = 'posts'
        
        # Ensure all required fields are present according to SocialBu API
        if 'accounts' not in data:
            logger.error("'accounts' field is missing in post data")
            raise SocialBuAPIError("'accounts' field is required")
        
        if 'content' not in data:
            logger.error("'content' field is missing in post data")
            raise SocialBuAPIError("'content' field is required")
        
        logger.info(f"Sending post creation request to {endpoint}")
        
        try:
            # Make the API call with the validated data
            result = self.make_request(endpoint, 'POST', data)
            logger.info(f"Post creation successful. Response: {json.dumps(result, indent=2)}")
            return result
        except SocialBuAPIError as e:
            logger.error(f"Post creation failed: {e.message}")
            raise
        except Exception as e:
            logger.error(f"Unexpected error during post creation: {str(e)}")
            raise SocialBuAPIError(f"Unexpected error during post creation: {str(e)}")
    
    def update_post(self, post_id, data):
        """Update a post in SocialBu API"""
        return self.make_request(f'posts/{post_id}', 'PUT', data)
    
    def delete_post(self, post_id):
        """Delete a post in SocialBu API"""
        return self.make_request(f'posts/{post_id}', 'DELETE')
    
    # Media
    def upload_media(self, file):
        """Upload media to SocialBu API"""
        files = {'media': file}
        return self.make_request('media', 'POST', {}, files)
    
    def get_media(self):
        """Get media from SocialBu API"""
        return self.make_request('media')
    
    def delete_media(self, media_id):
        """Delete media from SocialBu API"""
        return self.make_request(f'media/{media_id}', 'DELETE')
    
    # Accounts
    def get_accounts(self):
        """Get accounts from SocialBu API"""
        return self.make_request('accounts')
    
    def disconnect_account(self, account_id):
        """Disconnect an account from SocialBu API"""
        return self.make_request(f'accounts/{account_id}', 'DELETE')
    
    # Insights
    def get_insights(self):
        """Get insights from SocialBu API"""
        return self.make_request('insights')
    
    def get_post_insights(self, post_id):
        """Get post insights from SocialBu API"""
        return self.make_request(f'posts/{post_id}/insights')
    
    # Notifications
    def get_notifications(self):
        """Get notifications from SocialBu API"""
        return self.make_request('notifications')
    
    def mark_notification_as_read(self, notification_id):
        """Mark a notification as read in SocialBu API"""
        return self.make_request(f'notifications/{notification_id}', 'PUT', {'read': True})
    
    # Teams
    def create_team(self, name):
        """Create a team in SocialBu API"""
        return self.make_request('teams', 'POST', {'name': name})
    
    def add_team_member(self, team_id, user_id):
        """Add a team member in SocialBu API"""
        return self.make_request(f'teams/{team_id}/members', 'POST', {'user_id': user_id})
    
    def get_team_members(self, team_id):
        """Get team members from SocialBu API"""
        return self.make_request(f'teams/{team_id}/members')
    
    def remove_team_member(self, team_id, user_id):
        """Remove a team member from SocialBu API"""
        return self.make_request(f'teams/{team_id}/members/{user_id}', 'DELETE')


class SocialBuAPIError(Exception):
    """Exception raised for SocialBu API errors"""
    
    def __init__(self, message, status_code=None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

def get_socialbu_token_for_user(user):
    try:
        token_obj = SocialBuToken.objects.get(user=user)
        # Optionally: check if token is expired and refresh if needed
        return token_obj.access_token
    except SocialBuToken.DoesNotExist:
        # If you store SocialBu credentials on the user model
        if hasattr(user, 'socialbu_email') and hasattr(user, 'socialbu_password') and user.socialbu_email and user.socialbu_password:
            service = SocialBuService()
            result = service.authenticate(user.socialbu_email, user.socialbu_password)
            token = result['token']
            SocialBuToken.objects.create(user=user, access_token=token)
            return token
        else:
            raise Exception("No SocialBu token or credentials found for user")
 