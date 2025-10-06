# Use Python 3.11 slim image for smaller size
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV DEBIAN_FRONTEND=noninteractive

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
        build-essential \
        libpq-dev \
        curl \
        # Add a minimal text editor for debugging if needed, though often unnecessary
        # nano \
        && rm -rf /var/lib/apt/lists/*

# Create a non-root user
RUN adduser --disabled-password --gecos '' appuser

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Copy project files and start script
COPY . /app/

# Make the start script executable
RUN chmod +x /app/start.sh

# Create necessary directories
RUN mkdir -p /app/staticfiles /app/media /app/logs

# Set proper permissions
RUN chown -R appuser:appuser /app
USER appuser

# Expose port (optional, but good practice)
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health/ || exit 1

# No final CMD is needed, as startCommand="./start.sh" in railway.toml will execute it.