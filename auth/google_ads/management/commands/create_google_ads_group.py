from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from google_ads.models import Campaign, AdGroup, Ad, PerformanceReport, KeywordMetrics

class Command(BaseCommand):
    help = 'Creates the google_ads_managers group with appropriate permissions'

    def handle(self, *args, **options):
        # Create the group if it doesn't exist
        group, created = Group.objects.get_or_create(name='google_ads_managers')

        if created:
            self.stdout.write(self.style.SUCCESS('Successfully created google_ads_managers group'))
        else:
            self.stdout.write(self.style.WARNING('google_ads_managers group already exists'))

        # Get content types for our models
        models = [Campaign, AdGroup, Ad, PerformanceReport, KeywordMetrics]
        content_types = ContentType.objects.get_for_models(*models)

        # Define permissions we want to assign
        permissions = []
        for model in models:
            ct = content_types[model]
            model_permissions = Permission.objects.filter(
                content_type=ct,
                codename__in=[
                    f'add_{model._meta.model_name}',
                    f'change_{model._meta.model_name}',
                    f'delete_{model._meta.model_name}',
                    f'view_{model._meta.model_name}',
                ]
            )
            permissions.extend(model_permissions)

        # Assign permissions to the group
        group.permissions.set(permissions)
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully assigned {len(permissions)} permissions to google_ads_managers group'
            )
        ) 