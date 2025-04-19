from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.conf import settings
import os

User = get_user_model()

class Command(BaseCommand):
    help = 'Creates default admin users for the application'

    def add_arguments(self, parser):
        parser.add_argument(
            '--superadmin-email',
            default=os.getenv('SUPERADMIN_EMAIL', 'superadmin@linkly.com'),
            help='Email for the superadmin user'
        )
        parser.add_argument(
            '--superadmin-password',
            default=os.getenv('SUPERADMIN_PASSWORD', 'Linkly@2025!'),
            help='Password for the superadmin user'
        )
        parser.add_argument(
            '--admin-email',
            default=os.getenv('ADMIN_EMAIL', 'admin@linkly.com'),
            help='Email for the admin user'
        )
        parser.add_argument(
            '--admin-password',
            default=os.getenv('ADMIN_PASSWORD', 'Admin@2025!'),
            help='Password for the admin user'
        )
        parser.add_argument(
            '--no-input',
            action='store_true',
            help='Run without asking for confirmation'
        )

    def handle(self, *args, **options):
        if not options['no_input']:
            confirm = input(
                '\nYou are about to create admin users. '
                'This will overwrite existing users with the same emails.\n'
                'Do you want to continue? [y/N]: '
            )
            if confirm.lower() != 'y':
                self.stdout.write(self.style.WARNING('Operation cancelled.'))
                return

        # Create superadmin
        superadmin_email = options['superadmin_email']
        superadmin_password = options['superadmin_password']
        
        superadmin, created = User.objects.update_or_create(
            email=superadmin_email,
            defaults={
                'username': 'superadmin',
                'first_name': 'Super',
                'last_name': 'Admin',
                'is_active': True,
                'is_staff': True,
                'is_superuser': True,
                'date_joined': timezone.now()
            }
        )
        superadmin.set_password(superadmin_password)
        superadmin.save()

        action = 'Created' if created else 'Updated'
        self.stdout.write(
            self.style.SUCCESS(f'{action} superadmin user: {superadmin_email}')
        )

        # Create admin
        admin_email = options['admin_email']
        admin_password = options['admin_password']
        
        admin, created = User.objects.update_or_create(
            email=admin_email,
            defaults={
                'username': 'admin',
                'first_name': 'Admin',
                'last_name': 'User',
                'is_active': True,
                'is_staff': True,
                'is_superuser': True,
                'date_joined': timezone.now()
            }
        )
        admin.set_password(admin_password)
        admin.save()

        action = 'Created' if created else 'Updated'
        self.stdout.write(
            self.style.SUCCESS(f'{action} admin user: {admin_email}')
        )

        self.stdout.write(self.style.SUCCESS('Successfully created admin users.')) 