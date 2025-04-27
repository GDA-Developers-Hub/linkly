#!/bin/bash

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run migrations
python manage.py migrate

# Create superuser if it doesn't exist
echo "from django.contrib.auth import get_user_model; User = get_user_model(); User.objects.filter(email='admin@socialbu.com').exists() or User.objects.create_superuser('admin@socialbu.com', 'adminpassword')" | python manage.py shell

# Start server
python manage.py runserver 0.0.0.  'adminpassword')" | python manage.py shell

# Start server
python manage.py runserver 0.0.0.0:8000
