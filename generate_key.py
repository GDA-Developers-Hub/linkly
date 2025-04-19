from django.core.management.utils import get_random_secret_key

secret_key = get_random_secret_key()
print(f"Generated Secret Key: {secret_key}") 