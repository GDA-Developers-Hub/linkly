#!/bin/bash

# Exit if any command fails
set -e

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install dependencies if requirements.txt exists
if [ -f "requirements.txt" ]; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Run migrations
echo "Running migrations..."
python3 manage.py migrate


# Start the Django development server
echo "Starting server..."
python3 manage.py runserver 0.0.0.0:8000
