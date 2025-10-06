# Sales Management System

A Django-based sales management application for handling inventory, sales transactions, customer management, and business analytics.

![Python](https://img.shields.io/badge/Python-3.8+-blue)
![Django](https://img.shields.io/badge/Django-5.2+-green)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-Database-blue)
![License](https://img.shields.io/badge/License-MIT-yellow)

## 📋 Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Database Setup](#database-setup)
- [Running the Application](#running-the-application)
- [Project Structure](#project-structure)
- [API Documentation](#api-documentation)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

## ✨ Features

### 🏪 Store Management
- **Inventory Management**: Track products, categories, and stock levels
- **Vendor Management**: Manage supplier information and relationships
- **Category Organization**: Hierarchical product categorization
- **Stock Monitoring**: Real-time inventory tracking with low-stock alerts
- **Product Details**: Comprehensive product information with images

### 💰 Sales Management
- **Transaction Processing**: Complete sales workflow from quote to payment
- **Customer Management**: Detailed customer profiles and purchase history
- **Invoice Generation**: Automated invoice creation and management
- **Sales Analytics**: Revenue tracking and performance metrics
- **Tax Calculations**: Automated tax computation and reporting

### 👥 User Management
- **Role-Based Access**: Admin, Executive, and Operative user roles
- **User Profiles**: Detailed staff profiles with contact information
- **Authentication System**: Secure login with session management
- **Permission Control**: Granular access control based on user roles

### 📊 Analytics & Reporting
- **Sales Dashboard**: Visual analytics with charts and graphs
- **Revenue Reports**: Detailed financial reporting and analysis
- **Export Functions**: Excel/CSV export capabilities
- **Performance Metrics**: KPI tracking and business intelligence

### 🎨 User Interface
- **Responsive Design**: Mobile-first Bootstrap 5 interface
- **Dark/Light Theme**: Customizable UI themes
- **Interactive Charts**: Chart.js integration for data visualization
- **Modern UX**: Clean, intuitive user experience

## 🛠 Tech Stack

### Backend
- **Django 5.2+**: Web framework
- **PostgreSQL**: Primary database
- **Python 3.8+**: Programming language
- **Django REST Framework**: API development (if applicable)

### Frontend
- **Bootstrap 5**: CSS framework
- **Chart.js**: Data visualization
- **Font Awesome**: Icons
- **Crispy Forms**: Enhanced form rendering

### Additional Libraries
- **Pillow**: Image processing
- **django-imagekit**: Image optimization
- **django-tables2**: Enhanced table displays
- **django-filter**: Advanced filtering
- **phonenumber-field**: International phone number handling
- **python-decouple**: Environment configuration

## 📋 Prerequisites

Before you begin, ensure you have the following installed:

- **Python 3.8+** - [Download Python](https://python.org/downloads/)
- **PostgreSQL 12+** - [Download PostgreSQL](https://postgresql.org/download/)
- **Git** - [Download Git](https://git-scm.com/downloads)
- **pip** - Python package installer (comes with Python)
- **virtualenv** - Python virtual environment tool

### System Dependencies (Ubuntu/Debian)
```bash
sudo apt update
sudo apt install python3-dev python3-pip python3-venv postgresql postgresql-contrib libpq-dev
```

### System Dependencies (macOS)
```bash
brew install python postgresql
```

### System Dependencies (Windows)
- Install Python from python.org
- Install PostgreSQL from postgresql.org
- Install Git from git-scm.com

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/mburuxx/sales-management.git
cd sales-management
```

### 2. Create Virtual Environment
```bash
# Create virtual environment
python3 -m venv venv

# Activate virtual environment
# On Linux/macOS:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

## ⚙️ Configuration

### 1. Environment Variables

Create a `.env` file in the project root directory:

```bash
# Copy the example environment file
cp .env.example .env
```

Edit the `.env` file with your configuration:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=sales_management_db
DB_USER=your_db_user
DB_PASSWORD=your_db_password
DB_HOST=localhost
DB_PORT=5432

# Email Configuration (Optional)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=your-email@example.com
EMAIL_HOST_PASSWORD=your-email-password
EMAIL_USE_TLS=True

# Media and Static Files
MEDIA_ROOT=/path/to/media/files
STATIC_ROOT=/path/to/static/files
```

### 2. Generate Secret Key

Generate a new Django secret key:

```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

Copy the output and paste it as your `SECRET_KEY` in the `.env` file.

## 🗄️ Database Setup

### 1. Create PostgreSQL Database

```sql
-- Connect to PostgreSQL as superuser
sudo -u postgres psql

-- Create database and user
CREATE DATABASE sales_management_db;
CREATE USER your_db_user WITH PASSWORD 'your_db_password';

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE sales_management_db TO your_db_user;
ALTER USER your_db_user CREATEDB;

-- Exit PostgreSQL
\q
```

### 2. Run Migrations

```bash
# Navigate to Django project directory
cd salesmgt

# Create and apply migrations
python manage.py makemigrations
python manage.py migrate
```

### 3. Create Superuser

```bash
python manage.py createsuperuser
```

### 4. Load Initial Data (Optional)

```bash
# Load sample data if fixtures are available
python manage.py loaddata sales/fixtures/initial_data.json
```

## 🏃‍♂️ Running the Application

### Development Server

```bash
# Navigate to project directory
cd salesmgt

# Start development server
python manage.py runserver

# Access the application at:
# http://127.0.0.1:8000/
```

### Production Server

For production deployment, use a WSGI server like Gunicorn:

```bash
# Install Gunicorn
pip install gunicorn

# Run with Gunicorn
gunicorn salesmgt.wsgi:application --bind 0.0.0.0:8000
```

## 📁 Project Structure

```
sales-management/
├── README.md
├── requirements.txt
├── .env.example
├── .gitignore
└── salesmgt/
    ├── manage.py
    ├── salesmgt/
    │   ├── __init__.py
    │   ├── settings.py
    │   ├── urls.py
    │   ├── wsgi.py
    │   └── asgi.py
    ├── accounts/
    │   ├── models.py          # User profiles, vendors, customers
    │   ├── views.py           # Authentication and user management
    │   ├── forms.py           # User registration and profile forms
    │   ├── admin.py           # Admin interface configuration
    │   ├── urls.py            # URL routing
    │   ├── templates/         # HTML templates
    │   ├── migrations/        # Database migrations
    │   └── tests/             # Test suite
    ├── store/
    │   ├── models.py          # Products, categories, inventory
    │   ├── views.py           # Store management views
    │   ├── forms.py           # Product and category forms
    │   ├── admin.py           # Store admin interface
    │   ├── urls.py            # Store URL patterns
    │   ├── templates/         # Store templates
    │   ├── migrations/        # Database migrations
    │   └── tests/             # Comprehensive test suite
    ├── sales/
    │   ├── models.py          # Sales transactions and purchases
    │   ├── views.py           # Sales processing views
    │   ├── forms.py           # Sales and purchase forms
    │   ├── signals.py         # Inventory update signals
    │   ├── admin.py           # Sales admin interface
    │   ├── urls.py            # Sales URL patterns
    │   ├── templates/         # Sales templates
    │   ├── fixtures/          # Sample data
    │   ├── migrations/        # Database migrations
    │   └── tests/             # Comprehensive test suite
    ├── static/                # CSS, JavaScript, images
    ├── media/                 # User uploaded files
    └── profile_pics/          # User profile pictures
```

## 🔌 API Documentation

### Key Endpoints

#### Authentication
- `POST /accounts/login/` - User login
- `POST /accounts/register/` - User registration
- `POST /accounts/logout/` - User logout

#### Store Management
- `GET /store/` - List all products
- `GET /store/categories/` - List categories
- `GET /store/category/<slug>/` - Category details
- `POST /store/items/add/` - Add new product

#### Sales Management
- `GET /sales/` - Sales dashboard
- `POST /sales/add/` - Create new sale
- `GET /sales/export/` - Export sales data
- `GET /sales/purchase/` - Purchase management

### Response Formats

The API returns JSON responses in the following format:

```json
{
    "status": "success|error",
    "message": "Response message",
    "data": {
        // Response data
    }
}
```

## 🧪 Testing

The application includes test suites for all major components.

### Running Tests

```bash
# Run all tests
python manage.py test

# Run tests for specific app
python manage.py test accounts
python manage.py test store
python manage.py test sales

# Run specific test module
python manage.py test store.tests.test_models

# Run tests with coverage
pip install coverage
coverage run --source='.' manage.py test
coverage report
coverage html  # Generate HTML report
```

### Test Structure

Each app includes tests:

- **Model Tests**: Database models, validations, relationships
- **Form Tests**: Form validation, widget configuration
- **View Tests**: HTTP responses, permissions, authentication
- **URL Tests**: URL routing and reverse lookups
- **Signal Tests**: Django signals and business logic
- **Admin Tests**: Admin interface functionality

### Test Coverage

```bash
# Generate coverage report
coverage run manage.py test
coverage report --show-missing

# View detailed HTML report
coverage html
open htmlcov/index.html  # macOS
xdg-open htmlcov/index.html  # Linux
```

## 🚀 Deployment

### Environment Preparation

1. **Production Settings**
   ```python
   # In settings.py or create settings_prod.py
   DEBUG = False
   ALLOWED_HOSTS = ['your-domain.com', 'www.your-domain.com']
   
   # Database configuration for production
   DATABASES = {
       'default': {
           'ENGINE': 'django.db.backends.postgresql',
           'NAME': config('PROD_DB_NAME'),
           'USER': config('PROD_DB_USER'),
           'PASSWORD': config('PROD_DB_PASSWORD'),
           'HOST': config('PROD_DB_HOST'),
           'PORT': config('PROD_DB_PORT'),
       }
   }
   ```

2. **Collect Static Files**
   ```bash
   python manage.py collectstatic --noinput
   ```

### Deployment Options

#### 1. Heroku Deployment

```bash
# Install Heroku CLI and login
heroku login

# Create new Heroku app
heroku create your-sales-app

# Add PostgreSQL addon
heroku addons:create heroku-postgresql:hobby-dev

# Set environment variables
heroku config:set SECRET_KEY=your-secret-key
heroku config:set DEBUG=False

# Deploy
git push heroku main

# Run migrations
heroku run python manage.py migrate

# Create superuser
heroku run python manage.py createsuperuser
```

#### 2. Docker Deployment

Create `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["gunicorn", "salesmgt.wsgi:application", "--bind", "0.0.0.0:8000"]
```

Create `docker-compose.yml`:

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
    depends_on:
      - db

  db:
    image: postgres:13
    environment:
      POSTGRES_DB: sales_management_db
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
    volumes:
      - postgres_data:/var/lib/postgresql/data

volumes:
  postgres_data:
```

#### 3. Traditional Server Deployment

```bash
# Install required packages
sudo apt update
sudo apt install nginx postgresql supervisor

# Configure Gunicorn
pip install gunicorn
gunicorn salesmgt.wsgi:application --bind unix:/run/gunicorn.sock

# Configure Nginx
sudo nano /etc/nginx/sites-available/sales-management

# Configure Supervisor
sudo nano /etc/supervisor/conf.d/sales-management.conf
```

## 📚 Usage Guide

### Admin Interface

1. **Access Admin Panel**
   - Navigate to `http://your-domain.com/admin/`
   - Login with superuser credentials

2. **User Management**
   - Create user accounts and assign roles
   - Manage user profiles and permissions

3. **Store Management**
   - Add product categories and items
   - Manage vendor information
   - Track inventory levels

### Sales Workflow

1. **Customer Registration**
   - Register new customers or select existing ones
   - Maintain customer contact information

2. **Sales Process**
   - Select products and quantities
   - Calculate taxes and totals
   - Process payments and generate invoices

3. **Reporting**
   - View sales analytics and charts
   - Export sales data to Excel/CSV
   - Monitor business performance

## 🤝 Contributing

We welcome contributions to improve the Sales Management System!

### Development Setup

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Write/update tests
5. Submit a pull request

### Coding Standards

- Follow PEP 8 Python style guide
- Write comprehensive docstrings
- Include unit tests for new features
- Update documentation as needed

### Pull Request Process

1. Ensure all tests pass
2. Update README if needed
3. Add descriptive commit messages
4. Request code review

## 📝 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### Common Issues

1. **Database Connection Errors**
   - Verify PostgreSQL is running
   - Check database credentials in `.env`
   - Ensure database exists

2. **Migration Issues**
   ```bash
   # Reset migrations if needed
   python manage.py migrate --fake-initial
   ```

3. **Static Files Not Loading**
   ```bash
   # Collect static files
   python manage.py collectstatic
   ```

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/mburuxx/sales-management/issues)
- **Documentation**: Check this README and code comments
- **Community**: Join our discussions


## 🔒 Security

### Security Features

- CSRF protection enabled
- Secure password validation
- Role-based access control
- SQL injection prevention
- XSS protection

### Security Best Practices

1. **Production Security**
   - Set `DEBUG = False`
   - Use HTTPS in production
   - Implement proper error handling
   - Regular security updates

2. **Database Security**
   - Use strong database passwords
   - Limit database user permissions
   - Regular database backups

---

For more information, visit our [GitHub repository](https://github.com/mburuxx/sales-management) or contact the development team.