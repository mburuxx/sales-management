# Deployment Guide

This guide covers various deployment options for the Sales Management System in production environments.

## 📋 Table of Contents

- [Pre-deployment Checklist](#pre-deployment-checklist)
- [Environment Setup](#environment-setup)
- [Heroku Deployment](#heroku-deployment)
- [DigitalOcean Deployment](#digitalocean-deployment)
- [AWS Deployment](#aws-deployment)
- [Docker Deployment](#docker-deployment)
- [Traditional VPS Deployment](#traditional-vps-deployment)
- [Monitoring and Maintenance](#monitoring-and-maintenance)
- [Troubleshooting](#troubleshooting)

## 🚀 Pre-deployment Checklist

Before deploying to production, ensure you have:

### Security Checklist
- [ ] Set `DEBUG = False` in settings
- [ ] Use strong `SECRET_KEY` (different from development)
- [ ] Configure `ALLOWED_HOSTS` properly
- [ ] Set up HTTPS/SSL certificates
- [ ] Configure secure database credentials
- [ ] Enable CSRF protection
- [ ] Set secure cookie settings
- [ ] Configure proper file permissions

### Performance Checklist
- [ ] Configure static file serving (CDN/nginx)
- [ ] Set up database connection pooling
- [ ] Configure caching (Redis/Memcached)
- [ ] Optimize database queries
- [ ] Set up database backups
- [ ] Configure logging
- [ ] Set up monitoring

### Code Quality Checklist
- [ ] All tests pass
- [ ] Code review completed
- [ ] Dependencies updated
- [ ] Security vulnerabilities addressed
- [ ] Documentation updated

## ⚙️ Environment Setup

### Production Settings

Create `settings_production.py`:

```python
from .settings import *
import os

# Security Settings
DEBUG = False
ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': os.environ.get('DATABASE_URL'),
        'OPTIONS': {
            'sslmode': 'require',
        },
    }
}

# Static files
STATIC_ROOT = os.path.join(BASE_DIR, 'staticfiles')
STATICFILES_STORAGE = 'django.contrib.staticfiles.storage.StaticFilesStorage'

# Media files
MEDIA_ROOT = os.path.join(BASE_DIR, 'media')

# Security
SECURE_BROWSER_XSS_FILTER = True
SECURE_CONTENT_TYPE_NOSNIFF = True
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_SECONDS = 31536000
SECURE_REDIRECT_EXEMPT = []
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Logging
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'INFO',
            'class': 'logging.FileHandler',
            'filename': 'django.log',
        },
    },
    'loggers': {
        'django': {
            'handlers': ['file'],
            'level': 'INFO',
            'propagate': True,
        },
    },
}
```

### Environment Variables

```bash
# Production environment variables
export DJANGO_SETTINGS_MODULE=salesmgt.settings_production
export SECRET_KEY=your-production-secret-key
export DATABASE_URL=postgresql://user:password@host:port/database
export ALLOWED_HOSTS=your-domain.com,www.your-domain.com
export DEBUG=False
```

## 🌐 Heroku Deployment

### Prerequisites
- Heroku CLI installed
- Git repository
- Heroku account

### Step 1: Prepare Application

Create `Procfile`:
```
web: gunicorn salesmgt.wsgi:application --bind 0.0.0.0:$PORT
release: python salesmgt/manage.py migrate
```

Create `runtime.txt`:
```
python-3.11.0
```

Update `requirements.txt`:
```
# Add production dependencies
gunicorn==21.2.0
dj-database-url==2.1.0
whitenoise==6.6.0
psycopg2-binary==2.9.7
```

### Step 2: Configure Django for Heroku

Add to `settings.py`:
```python
import dj_database_url

# Heroku database configuration
DATABASES['default'] = dj_database_url.config(
    default=DATABASES['default']
)

# Static files
MIDDLEWARE.insert(1, 'whitenoise.middleware.WhiteNoiseMiddleware')
STATICFILES_STORAGE = 'whitenoise.storage.CompressedManifestStaticFilesStorage'
```

### Step 3: Deploy to Heroku

```bash
# Login to Heroku
heroku login

# Create Heroku app
heroku create your-sales-app

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:mini

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False

# Deploy
git add .
git commit -m "Prepare for Heroku deployment"
git push heroku main

# Run migrations
heroku run python salesmgt/manage.py migrate

# Create superuser
heroku run python salesmgt/manage.py createsuperuser

# Open application
heroku open
```

## 🌊 DigitalOcean Deployment

### Using App Platform

1. **Create App**
   - Connect GitHub repository
   - Select branch (usually `main`)
   - Configure build settings

2. **Environment Variables**
   ```
   SECRET_KEY=your-secret-key
   DEBUG=False
   DATABASE_URL=postgresql://user:pass@host:port/db
   ```

3. **Database Setup**
   - Create Managed PostgreSQL database
   - Connect to application

### Using Droplets

```bash
# Create Ubuntu 20.04 droplet
# SSH into droplet

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-pip python3-dev python3-venv
sudo apt install postgresql postgresql-contrib nginx

# Setup application
git clone https://github.com/yourusername/sales-management.git
cd sales-management
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure nginx
sudo nano /etc/nginx/sites-available/sales-management

# Configure gunicorn
pip install gunicorn
gunicorn --bind 0.0.0.0:8000 salesmgt.wsgi:application
```

## ☁️ AWS Deployment

### Using Elastic Beanstalk

1. **Install EB CLI**
   ```bash
   pip install awsebcli
   ```

2. **Initialize Application**
   ```bash
   eb init sales-management
   eb create production
   ```

3. **Configure Environment**
   ```bash
   eb setenv SECRET_KEY=your-secret-key
   eb setenv DEBUG=False
   eb setenv RDS_DB_NAME=your-db-name
   ```

### Using EC2 with RDS

```bash
# Launch EC2 instance
# Create RDS PostgreSQL instance
# Configure security groups

# Setup application on EC2
sudo yum update -y
sudo yum install python3-pip git nginx -y

# Clone and setup application
git clone https://github.com/yourusername/sales-management.git
cd sales-management
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Configure for production
export RDS_HOSTNAME=your-rds-endpoint
export RDS_PORT=5432
export RDS_DB_NAME=your-db-name
export RDS_USERNAME=your-username
export RDS_PASSWORD=your-password
```

## 🐳 Docker Deployment

### Dockerfile

```dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Set work directory
WORKDIR /app

# Install system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy project
COPY . /app/

# Collect static files
RUN python salesmgt/manage.py collectstatic --noinput

# Run gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "salesmgt.wsgi:application"]
```

### docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - SECRET_KEY=your-secret-key
      - DATABASE_URL=postgresql://postgres:password@db:5432/sales_db
    depends_on:
      - db
    volumes:
      - static_volume:/app/staticfiles
      - media_volume:/app/media

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: sales_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

  nginx:
    image: nginx:alpine
    ports:
      - "80:80"
      - "443:443"
    volumes:
      - ./nginx.conf:/etc/nginx/nginx.conf
      - static_volume:/app/staticfiles
      - media_volume:/app/media
    depends_on:
      - web

volumes:
  postgres_data:
  static_volume:
  media_volume:
```

### Deploy with Docker

```bash
# Build and run
docker-compose up -d --build

# Run migrations
docker-compose exec web python salesmgt/manage.py migrate

# Create superuser
docker-compose exec web python salesmgt/manage.py createsuperuser

# View logs
docker-compose logs -f
```

## 🖥️ Traditional VPS Deployment

### Ubuntu 20.04 Setup

```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3-pip python3-dev python3-venv
sudo apt install postgresql postgresql-contrib
sudo apt install nginx supervisor

# Create user
sudo adduser salesapp
sudo usermod -aG sudo salesapp

# Setup application
sudo su - salesapp
git clone https://github.com/yourusername/sales-management.git
cd sales-management
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
pip install gunicorn
```

### Configure Gunicorn

Create `/etc/supervisor/conf.d/sales-management.conf`:

```ini
[program:sales-management]
command=/home/salesapp/sales-management/venv/bin/gunicorn salesmgt.wsgi:application
directory=/home/salesapp/sales-management/salesmgt
user=salesapp
autostart=true
autorestart=true
redirect_stderr=true
stdout_logfile=/var/log/sales-management.log
```

### Configure Nginx

Create `/etc/nginx/sites-available/sales-management`:

```nginx
server {
    listen 80;
    server_name your-domain.com www.your-domain.com;

    location = /favicon.ico { access_log off; log_not_found off; }
    
    location /static/ {
        root /home/salesapp/sales-management/salesmgt;
    }
    
    location /media/ {
        root /home/salesapp/sales-management/salesmgt;
    }

    location / {
        include proxy_params;
        proxy_pass http://unix:/home/salesapp/sales-management/sales-management.sock;
    }
}
```

Enable the site:
```bash
sudo ln -s /etc/nginx/sites-available/sales-management /etc/nginx/sites-enabled
sudo nginx -t
sudo systemctl restart nginx
```

## 📊 Monitoring and Maintenance

### Health Checks

Create `health_check.py`:
```python
#!/usr/bin/env python
import requests
import sys

def check_application():
    try:
        response = requests.get('https://your-domain.com/health/', timeout=30)
        if response.status_code == 200:
            print("✅ Application is healthy")
            return True
        else:
            print(f"❌ Application returned {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Health check failed: {e}")
        return False

if __name__ == "__main__":
    if not check_application():
        sys.exit(1)
```

### Backup Script

Create `backup.sh`:
```bash
#!/bin/bash

# Database backup
pg_dump $DATABASE_URL > "backup_$(date +%Y%m%d_%H%M%S).sql"

# Media files backup
tar -czf "media_backup_$(date +%Y%m%d_%H%M%S).tar.gz" media/

# Upload to S3 (optional)
# aws s3 cp backup_*.sql s3://your-backup-bucket/
# aws s3 cp media_backup_*.tar.gz s3://your-backup-bucket/

# Clean old backups (keep last 7 days)
find . -name "backup_*.sql" -mtime +7 -delete
find . -name "media_backup_*.tar.gz" -mtime +7 -delete
```

### Monitoring with New Relic

```python
# Add to settings.py
import newrelic.agent

# New Relic configuration
newrelic.agent.initialize('newrelic.ini')

# Wrap WSGI application
from django.core.wsgi import get_wsgi_application
application = newrelic.agent.WSGIApplicationWrapper(get_wsgi_application())
```

## 🔧 Troubleshooting

### Common Issues

1. **Static Files Not Loading**
   ```bash
   python manage.py collectstatic --clear
   python manage.py collectstatic --noinput
   ```

2. **Database Connection Errors**
   ```bash
   # Check database connectivity
   python manage.py dbshell
   
   # Check environment variables
   echo $DATABASE_URL
   ```

3. **Migration Issues**
   ```bash
   # Check migration status
   python manage.py showmigrations
   
   # Apply migrations
   python manage.py migrate --fake-initial
   ```

4. **Memory Issues**
   ```bash
   # Check memory usage
   free -h
   
   # Restart services
   sudo systemctl restart gunicorn
   sudo systemctl restart nginx
   ```

### Performance Optimization

1. **Database Optimization**
   ```sql
   -- Add indexes for frequently queried fields
   CREATE INDEX idx_sale_date ON sales_sale(date_added);
   CREATE INDEX idx_customer_name ON accounts_customer(name);
   ```

2. **Caching Setup**
   ```python
   # Redis caching
   CACHES = {
       'default': {
           'BACKEND': 'django_redis.cache.RedisCache',
           'LOCATION': 'redis://127.0.0.1:6379/1',
           'OPTIONS': {
               'CLIENT_CLASS': 'django_redis.client.DefaultClient',
           }
       }
   }
   ```

3. **CDN Setup**
   ```python
   # AWS S3 + CloudFront
   DEFAULT_FILE_STORAGE = 'storages.backends.s3boto3.S3Boto3Storage'
   STATICFILES_STORAGE = 'storages.backends.s3boto3.S3StaticStorage'
   
   AWS_ACCESS_KEY_ID = 'your-access-key'
   AWS_SECRET_ACCESS_KEY = 'your-secret-key'
   AWS_STORAGE_BUCKET_NAME = 'your-bucket-name'
   ```

### Log Analysis

```bash
# Application logs
tail -f /var/log/sales-management.log

# Nginx logs
tail -f /var/log/nginx/access.log
tail -f /var/log/nginx/error.log

# PostgreSQL logs
sudo tail -f /var/log/postgresql/postgresql-*.log

# System logs
journalctl -u gunicorn -f
```

## 📝 Deployment Checklist

### Pre-deployment
- [ ] Code tested and reviewed
- [ ] Environment variables configured
- [ ] Database backup created
- [ ] Dependencies updated
- [ ] Security settings verified

### During Deployment
- [ ] Application deployed successfully
- [ ] Database migrations applied
- [ ] Static files collected
- [ ] Services restarted
- [ ] Health checks passing

### Post-deployment
- [ ] Application accessible
- [ ] All features working
- [ ] Performance monitoring active
- [ ] Backup systems operational
- [ ] Team notified of deployment

---

**Need help with deployment? Check our troubleshooting section or contact the development team.**