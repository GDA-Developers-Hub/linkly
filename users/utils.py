from django.conf import settings
from django.core.cache import cache
import stripe

def get_stripe_instance():
    """
    Get a configured Stripe instance using environment variables.
    Uses caching to avoid reading env variables repeatedly.
    """
    stripe.api_key = settings.STRIPE_SECRET_KEY
    return stripe

def get_stripe_public_key():
    """
    Safely get the Stripe publishable key.
    """
    return settings.STRIPE_PUBLIC_KEY 