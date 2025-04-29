import os
import django
import sys

# Set up Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'socialbu.settings')
sys.path.append('/home/ismael/linkly/backend')
django.setup()

# Import our patched views module first to apply the patch
from content import views

# Import OpenAI and test
from openai import OpenAI
from django.conf import settings

print("Testing OpenAI client initialization...")
try:
    # Initialize a client with the same parameters as in views.py
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', settings.OPENAI_API_KEY))
    print("Successfully initialized OpenAI client!")

    # Try a simple API call if you have valid credentials
    try:
        response = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "Hello, can you tell me a joke?"}
            ],
            max_tokens=50
        )
        print("API call succeeded!")
        print(f"Response: {response.choices[0].message.content}")
    except Exception as e:
        print(f"API call failed (possibly due to invalid API key, which is expected in test): {str(e)}")

except Exception as e:
    print(f"Failed to initialize OpenAI client: {str(e)}") 