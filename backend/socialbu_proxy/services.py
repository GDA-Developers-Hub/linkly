import requests
import json
import logging
import string
import random
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import SocialBuToken
from datetime import datetime

User = get_user_model()
logger = logging.getLogger(__name__)

# Add a custom JSON encoder that can handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def generate_secure_password(length=16):
    """Generate a secure random password"""
    characters = string.ascii_letters + string.digits + string.punctuation
    password = ''.join(random.choice(characters) for i in range(length))
    return password

# Error Handling
class SocialBuAPIError(Exception):
    """Exception raised for SocialBu API errors"""
    def __init__(self, message, status_code=None):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)

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
            'Accept': 'application/json',  # Explicitly request JSON response
        }
        
        if self.token:
            # Ensure the token is properly formatted
            token = self.token.strip()
            headers['Authorization'] = f'Bearer {token}'
            logger.info(f"Using authorization token: {token[:10]}...")
        else:
            logger.warning("No authorization token available!")
            
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
        
        # Pre-process data to convert datetime objects to strings
        if data and not files:
            # Convert any datetime objects to strings
            processed_data = self._prepare_data_for_json(data)
        else:
            processed_data = data
        
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
                    # Use standard json parameter with processed data
                    response = requests.post(url, headers=headers, json=processed_data, timeout=30)
            elif method == 'PUT':
                # Use standard json parameter with processed data
                response = requests.put(url, headers=headers, json=processed_data, timeout=30)
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
            
            # Check if the response is JSON before trying to parse it
            content_type = response.headers.get('Content-Type', '')
            if 'application/json' not in content_type:
                # If the response is not JSON, raise an exception with the response text
                logger.error(f"Expected JSON response but got {content_type}. Response text: {response.text[:200]}...")
                raise SocialBuAPIError(f"API returned non-JSON response: {response.text[:100]}...", response.status_code)
            
            try:
                result = response.json()
                logger.info(f"SocialBu API Response data: {result}")
                return result
            except ValueError as e:
                # Failed to parse JSON
                logger.error(f"Failed to parse JSON response: {str(e)}")
                logger.error(f"Response content: {response.text[:200]}...")  # Log first 200 chars
                raise SocialBuAPIError(f"Invalid JSON response: {str(e)}", response.status_code)
                
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
    
    def _prepare_data_for_json(self, data):
        """Convert data with datetime objects to JSON-serializable format"""
        if isinstance(data, dict):
            result = {}
            for key, value in data.items():
                result[key] = self._prepare_data_for_json(value)
            return result
        elif isinstance(data, list):
            return [self._prepare_data_for_json(item) for item in data]
        elif isinstance(data, datetime):
            return data.isoformat()
        else:
            return data
    
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
            
            # Check if BASE_URL already includes /api/v1 to avoid duplication
            if self.BASE_URL.endswith('/api/v1'):
                url = f"{self.BASE_URL.rstrip('/')}/{endpoint}"
            else:
                url = f"{self.BASE_URL}/api/v1/{endpoint}"
                
            logger.info(f"Authentication endpoint: {endpoint}")
            logger.info(f"Full authentication URL: {url}")
                
            # Direct HTTP call to avoid URL construction issues
            headers = {
                'Content-Type': 'application/json',
            }
            
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            
            # Parse the response
            result = response.json()
            
            logger.info(f"Authentication result: {result}")
            
            # Map the response fields to our expected format
            return {
                'token': result.get('authToken') or result.get('token') or result.get('access_token'),
                'user_id': result.get('id') or result.get('user_id'),
                'name': result.get('name'),
                'email': result.get('email'),
                'verified': result.get('verified', False)
            }
        except requests.exceptions.RequestException as e:
            logger.error(f"Authentication request error: {str(e)}")
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

    def upload_media(self, file):
        """Upload media to SocialBu API's official media endpoint"""
        try:
            # Step 1: Get the signed URL and secure key
            file_data = {
                'name': file.name,
                'mime_type': file.content_type
            }
            
            # Make request to SocialBu's upload_media endpoint
            response = self.make_request('upload_media', method='POST', data=file_data, files={
                'file': (file.name, file.read(), file.content_type)
            })
            
            # Reset file pointer to beginning for second upload
            file.seek(0)
            
            # Validate the response
            if not isinstance(response, dict):
                raise SocialBuAPIError("Invalid response format from SocialBu media endpoint")
                
            if 'secure_key' not in response or 'signed_url' not in response:
                raise SocialBuAPIError("Missing secure_key or signed_url in response")

            # Step 2: Upload the file to the signed URL
            try:
                # Make a PUT request to the signed URL with the file content
                upload_response = requests.put(
                    response['signed_url'],
                    data=file.read(),
                    headers={
                        'Content-Type': file.content_type,
                        'x-amz-acl': 'private'
                    }
                )
                upload_response.raise_for_status()
                
                logger.info(f"File uploaded successfully to signed URL with status: {upload_response.status_code}")
            except Exception as e:
                logger.error(f"Error uploading to signed URL: {str(e)}")
                raise SocialBuAPIError(f"Failed to upload file content: {str(e)}")
                
            # Return the media info in the expected format
            return {
                'id': response['secure_key'],
                'url': response.get('url', ''),
                'type': file.content_type,
                'name': file.name,
                'upload_token': response['secure_key'],
                'secure_key': response['secure_key'],
                'key': response.get('key', ''),
                'signed_url': response.get('signed_url', ''),
                'created_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error uploading media: {str(e)}")
            if isinstance(e, SocialBuAPIError):
                raise
            raise SocialBuAPIError(f"Failed to upload media: {str(e)}")
    
    def create_post(self, data):
        """Create a post in SocialBu API"""
        # Log the data with proper datetime handling
        try:
            # Create a copy of the data for logging
            log_data = data.copy() if hasattr(data, 'copy') else dict(data)
            
            # Convert datetime objects to ISO format strings
            if 'publish_at' in log_data and log_data['publish_at']:
                log_data['publish_at'] = log_data['publish_at'].isoformat()
                
            logger.info(f"Creating post with data: {json.dumps(log_data, indent=2)}")
        except Exception as e:
            # Don't let logging errors block the API call
            logger.warning(f"Error logging post data: {str(e)}")
        
        # Make sure we're using the correct endpoint as per the requirements
        endpoint = 'posts'
        
        # Validate request according to SocialBu API documentation
        if 'accounts' not in data:
            logger.error("'accounts' field is missing in post data")
            raise SocialBuAPIError("'accounts' field is required")
        
        if not data.get('accounts') or not isinstance(data['accounts'], list) or len(data['accounts']) == 0:
            logger.error("'accounts' field must be a non-empty array")
            raise SocialBuAPIError("'accounts' field must be a non-empty array")
        
        if 'content' not in data and not data.get('existing_attachments'):
            logger.error("Either 'content' or media attachments are required")
            raise SocialBuAPIError("Either 'content' or media attachments are required")
        
        # Format request data according to platform requirements
        request_data = {
            'team_id': data.get('team_id', 0),
            'content': data.get('content', ''),
            'draft': data.get('draft', False),
            'accounts': data['accounts']
        }

        # Handle platform-specific options
        platform = data.get('platform', '').lower()
        options = data.get('options', {})

        if platform == 'facebook':
            # Facebook-specific options
            request_data['options'] = {
                'comment': options.get('comment', ''),
                'post_as_story': options.get('post_as_story', False)
            }
        elif platform == 'twitter':
            # Twitter-specific options
            twitter_options = {}
            
            # Handle media alt text
            if 'media_alt_text' in options:
                twitter_options['media_alt_text'] = options['media_alt_text']
            
            # Handle threaded replies
            if 'threaded_replies' in options:
                twitter_options['threaded_replies'] = options['threaded_replies']
            
            if twitter_options:
                request_data['options'] = twitter_options

        # Add postback_url if provided
        if data.get('postback_url'):
            request_data['postback_url'] = data['postback_url']

        # Handle publish_at datetime
        if 'publish_at' in data and data['publish_at']:
            if isinstance(data['publish_at'], str):
                # Verify it matches the required format (YYYY-MM-DD HH:MM:SS)
                import re
                if re.match(r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$', data['publish_at']):
                    request_data['publish_at'] = data['publish_at']
                else:
                    try:
                        dt = datetime.fromisoformat(data['publish_at'].replace('Z', '+00:00'))
                        request_data['publish_at'] = dt.strftime('%Y-%m-%d %H:%M:%S')
                    except Exception as e:
                        raise SocialBuAPIError(f"Invalid publish_at format. Must be 'Y-m-d H:i:s' (e.g. '2025-04-30 17:25:00')")
            elif hasattr(data['publish_at'], 'strftime'):
                request_data['publish_at'] = data['publish_at'].strftime('%Y-%m-%d %H:%M:%S')
            else:
                raise SocialBuAPIError(f"Invalid publish_at format. Must be 'Y-m-d H:i:s' (e.g. '2025-04-30 17:25:00')")

        # Handle media attachments
        if data.get('existing_attachments'):
            if isinstance(data['existing_attachments'], list):
                formatted_attachments = []
                for item in data['existing_attachments']:
                    if isinstance(item, dict) and 'upload_token' in item:
                        formatted_attachments.append(item)
                    elif isinstance(item, str):
                        formatted_attachments.append({'upload_token': item})
                    else:
                        logger.warning(f"Skipping invalid attachment: {item}")
                request_data['existing_attachments'] = formatted_attachments
            else:
                request_data['existing_attachments'] = [{'upload_token': str(data['existing_attachments'])}]
        
        try:
            # Make the API call with the validated data
            result = self.make_request(endpoint, 'POST', request_data)
            logger.info(f"Post creation successful. Response: {json.dumps(result, indent=2)}")
            return result
        except SocialBuAPIError as e:
            logger.error(f"Post creation failed: {e.message}")
            if 'non-JSON response' in e.message and 'DOCTYPE html' in e.message:
                logger.error("Received HTML response instead of JSON. Authentication might have expired.")
                raise SocialBuAPIError("SocialBu authentication has expired or is invalid. Please re-authenticate.", 401)
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

# Standalone utility function

def get_socialbu_token_for_user(user):
    """
    Get the SocialBu token for a given user.
    Returns None if no token exists.
    """
    try:
        token_obj = SocialBuToken.objects.get(user=user)
        return token_obj.access_token
    except SocialBuToken.DoesNotExist:
        return None