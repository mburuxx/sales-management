#!/bin/bash
set -e

echo "🚀 Starting Sales Management System..."

# Navigate to Django project
cd salesmgt

echo "📊 Running database migrations..."
python manage.py migrate --noinput

echo "📁 Collecting static files..."
python manage.py collectstatic --noinput --clear

echo "🌐 Starting web server..."
exec gunicorn salesmgt.wsgi:application \
    --bind 0.0.0.0:$PORT \
    --workers 2 \
    --timeout 120 \
    --log-file - \
    --log-level info