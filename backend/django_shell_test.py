"""
This file contains code to test the hashtag generator from Django shell.

To use:
1. Start Django shell:
   python manage.py shell

2. Copy and paste the code below into the shell:

from content.views import GenerateHashtagsView
from content.serializers import HashtagGenerateSerializer
from rest_framework.test import APIRequestFactory
from django.contrib.auth import get_user_model
from rest_framework.test import force_authenticate

# Get a user (replace with an existing user's username)
User = get_user_model()
user = User.objects.get(username='your_username')

# Create a fake request
factory = APIRequestFactory()
view = GenerateHashtagsView.as_view()

# Create request data
data = {
    "query": "travel photography",
    "platform": "instagram",
    "count": 10,
    "content_type": "General Post",
    "popularity_mix": "balanced"
}

# Make a request
request = factory.post('/api/content/generate-hashtags/', data, format='json')
force_authenticate(request, user=user)
response = view(request)

# Print results
print("\nGenerated Hashtags:")
for hashtag in response.data.get("hashtags", []):
    print(f"#{hashtag['name']}")
print(f"\nTokens used: {response.data.get('tokens_used', 'N/A')}")
""" 