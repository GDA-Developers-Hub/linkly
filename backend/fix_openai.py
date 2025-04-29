import django
import os
import sys

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'socialbu.settings')
sys.path.append('/home/ismael/linkly/backend')
django.setup()

from django.conf import settings
import inspect

# Import OpenAI classes
from openai import OpenAI
from openai._base_client import BaseClient

# Print current OpenAI version
import openai
print(f"OpenAI library version: {openai.__version__}")

# Backup the original __init__ method
original_init = BaseClient.__init__

# Create a wrapper function that removes the 'proxies' parameter
def patched_init(self, *args, **kwargs):
    # Remove 'proxies' parameter if present
    if 'proxies' in kwargs:
        print(f"Removing 'proxies' parameter from OpenAI client initialization")
        del kwargs['proxies']
    
    # Call the original __init__ method
    return original_init(self, *args, **kwargs)

# Apply the monkey patch
BaseClient.__init__ = patched_init

print("OpenAI BaseClient.__init__ has been patched to remove 'proxies' parameter")

# Display the current signature
print(f"Current BaseClient.__init__ signature: {inspect.signature(BaseClient.__init__)}")

# This is just a test - now you can create a new OpenAI client
try:
    print("\nInitializing OpenAI client...")
    client = OpenAI(api_key=os.environ.get('OPENAI_API_KEY', settings.OPENAI_API_KEY))
    print("OpenAI client initialized successfully!")
    
    # Test a simple API call
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Say hello!"}
        ],
        max_tokens=10
    )
    print(f"Response: {response.choices[0].message.content}")
    
except Exception as e:
    print(f"Error: {e}")

# Add these lines to your content/views.py before importing OpenAI:
#
# # Patch the OpenAI BaseClient to remove 'proxies' parameter
# from openai._base_client import BaseClient
# original_init = BaseClient.__init__
# def patched_init(self, *args, **kwargs):
#     if 'proxies' in kwargs:
#         del kwargs['proxies']
#     return original_init(self, *args, **kwargs)
# BaseClient.__init__ = patched_init 