#!/bin/bash
# start.sh

# Change to the Django project directory
cd /app/salesmgt

# Apply database migrations
echo "Applying database migrations..."
python manage.py migrate --noinput

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn server
echo "Starting Gunicorn..."
# Use the same command from your Dockerfile's CMD
exec gunicorn --bind 0.0.0.0:8000 --workers 2 --timeout 120 salesmgt.wsgi:application