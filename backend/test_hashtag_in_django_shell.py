"""
Copy and paste the following code into the Django shell:

python3 manage.py shell

Then paste this code:
"""

from content.views import GenerateHashtagsView
from rest_framework.test import APIRequestFactory
from django.contrib.auth import get_user_model
import json

# Get the first user from the database
User = get_user_model()
user = User.objects.first()

if not user:
    print("No users found in the database. Please create a user first.")
else:
    print(f"Testing with user: {user.username}")
    
    # Create a test request
    factory = APIRequestFactory()
    view = GenerateHashtagsView.as_view()
    
    # Prepare the request data
    data = {
        "query": "travel photography",
        "platform": "instagram",
        "count": 5,
        "content_type": "General Post",
        "popularity_mix": "balanced"
    }
    
    # Make the request
    request = factory.post('/api/content/generate-hashtags/', 
                         data=json.dumps(data),
                         content_type='application/json')
    
    # Authenticate the request
    request.user = user
    
    # Call the view directly
    response = view(request)
    
    # Check the result
    if hasattr(response, 'status_code') and response.status_code == 200:
        print("\nGenerated Hashtags:")
        for hashtag in response.data.get("hashtags", []):
            print(f"#{hashtag['name']}")
        
        print(f"\nTokens used: {response.data.get('tokens_used', 'N/A')}")
    else:
        if hasattr(response, 'data'):
            print(f"Error: {response.data}")
        else:
            print(f"Error: {response}") 