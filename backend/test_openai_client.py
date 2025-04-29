from openai import OpenAI
import os
from django.conf import settings
import django
import sys

# Set up Django environment
sys.path.append('/home/ismael/linkly/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'socialbu.settings')
django.setup()

# Now you can import Django settings
from django.conf import settings

# Initialize OpenAI client
client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', settings.OPENAI_API_KEY))

# Test the client with a simple request
try:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, can you generate a test hashtag for me?"}
        ],
        max_tokens=50
    )
    
    print("OpenAI client is working correctly!")
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"Error: {str(e)}")
    print("OpenAI client initialization failed.") 