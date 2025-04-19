from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import User

@receiver(post_save, sender=User)
def send_welcome_email(sender, instance, created, **kwargs):
    """
    Send a welcome email when a new user is created
    """
    if created:
        try:
            send_mail(
                'Welcome to Linkly!',
                f'Hi {instance.username},\n\nWelcome to Linkly! We\'re excited to have you on board.',
                settings.EMAIL_HOST_USER,
                [instance.email],
                fail_silently=True,
            )
        except Exception:
            pass  # Fail silently if email sending fails

@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Initialize user profile data when a new user is created
    """
    if created:
        # Initialize any default values or related models if needed
        instance.metrics_last_updated = None
        instance.save() 