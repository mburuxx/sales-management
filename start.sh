#!/bin/sh
# Exit immediately if a command exits with a non-zero status.
set -e

# Change to the directory containing manage.py
cd /app/salesmgt

# Run database migrations
echo "Applying database migrations..."
python manage.py migrate

# Collect static files
echo "Collecting static files..."
python manage.py collectstatic --noinput

# Start Gunicorn server from the project root directory
# The wsgi module is located at salesmgt.wsgi
cd /app
echo "Starting Gunicorn..."
gunicorn salesmgt.wsgi:application --bind 0.0.0.0:$PORT --workers 3 --log-file -