import jwt
from django.conf import settings
from django.contrib.auth import get_user_model
from .models import SocialBuToken

User = get_user_model()

class SocialBuTokenMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Extract the Authorization header
        auth_header = request.META.get('HTTP_AUTHORIZATION', '')
        if auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
            try:
                # Decode the JWT (adjust algorithm and secret as needed)
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
                user_id = payload.get('user_id') or payload.get('sub')
                if user_id:
                    try:
                        user = User.objects.get(id=user_id)
                        request.socialbu_user_email = user.email
                        # Fetch SocialBu token
                        try:
                            socialbu_token = SocialBuToken.objects.get(user=user)
                            request.socialbu_token = socialbu_token.access_token
                        except SocialBuToken.DoesNotExist:
                            request.socialbu_token = None
                    except User.DoesNotExist:
                        request.socialbu_user_email = None
                        request.socialbu_token = None
            except Exception as e:
                # Invalid token or decode error
                request.socialbu_user_email = None
                request.socialbu_token = None
        else:
            request.socialbu_user_email = None
            request.socialbu_token = None

        return self.get_response(request) 