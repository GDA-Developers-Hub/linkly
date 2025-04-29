import os
import django
import sys

# Set up Django environment
sys.path.append('/home/ismael/linkly/backend')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'socialbu.settings')
django.setup()

from django.conf import settings
from openai import OpenAI

# Initialize OpenAI client with debug info
print("OpenAI package version:")
import openai
print(openai.__version__)

print("\nInitializing OpenAI client...")
try:
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', settings.OPENAI_API_KEY))
    print("OpenAI client initialized successfully!")
    
    # Test the client
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello, world!"}
        ],
        max_tokens=10
    )
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"Error initializing OpenAI client: {e}")
    
    # Print relevant information
    import inspect
    print("\nOpenAI client initialization signature:")
    print(inspect.signature(OpenAI.__init__)) 