FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libpq-dev gcc curl \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copy dependency files first (for better caching)
COPY requirements.txt /app/

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

COPY . /app/

# Create non-root user
RUN useradd -m appuser && chown -R appuser:appuser /app
USER appuser

WORKDIR /app/salesmgt

# Railway provides PORT environment variable
EXPOSE $PORT

# Remove the localhost healthcheck since Railway handles this
# HEALTHCHECK removed - Railway will handle health checks

# Fixed CMD with proper Railway port and setup commands
CMD ["sh", "-c", "python manage.py migrate --noinput && python manage.py collectstatic --noinput --clear && gunicorn salesmgt.wsgi:application --bind 0.0.0.0:$PORT --workers 2 --timeout 120 --log-file -"]