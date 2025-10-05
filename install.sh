#!/bin/bash

# Sales Management System - Quick Installation Script
# This script helps you set up the development environment quickly

set -e  # Exit on any error

echo "🚀 Sales Management System - Quick Setup"
echo "========================================"
echo

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if Python is installed
check_python() {
    print_status "Checking Python installation..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        print_success "Python $PYTHON_VERSION found"
    else
        print_error "Python 3 is not installed. Please install Python 3.8+ and try again."
        exit 1
    fi
}

# Check if PostgreSQL is installed
check_postgresql() {
    print_status "Checking PostgreSQL installation..."
    if command -v psql &> /dev/null; then
        POSTGRES_VERSION=$(psql --version | cut -d' ' -f3)
        print_success "PostgreSQL $POSTGRES_VERSION found"
    else
        print_warning "PostgreSQL not found. Please install PostgreSQL and try again."
        echo "  Ubuntu/Debian: sudo apt install postgresql postgresql-contrib"
        echo "  macOS: brew install postgresql"
        echo "  Windows: Download from https://postgresql.org/download/"
        exit 1
    fi
}

# Create virtual environment
create_venv() {
    print_status "Creating virtual environment..."
    if [ ! -d "venv" ]; then
        python3 -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
}

# Activate virtual environment and install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    # Activate virtual environment
    source venv/bin/activate
    
    # Upgrade pip
    pip install --upgrade pip
    
    # Install requirements
    pip install -r requirements.txt
    
    print_success "Dependencies installed successfully"
}

# Setup environment file
setup_env() {
    print_status "Setting up environment configuration..."
    
    if [ ! -f ".env" ]; then
        cp .env.example .env
        print_success "Environment file created from template"
        
        # Generate secret key
        SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
        
        # Update .env file with generated secret key
        if command -v sed &> /dev/null; then
            sed -i "s/your-secret-key-here-replace-with-actual-secret-key/$SECRET_KEY/" .env
            print_success "Secret key generated and added to .env file"
        else
            print_warning "Please update the SECRET_KEY in .env file manually"
        fi
        
        echo
        print_warning "Please update the database configuration in .env file:"
        echo "  - DB_NAME: Your database name"
        echo "  - DB_USER: Your database user"
        echo "  - DB_PASSWORD: Your database password"
        echo
    else
        print_warning "Environment file already exists"
    fi
}

# Create database
create_database() {
    print_status "Setting up database..."
    
    # Check if .env file exists and has database config
    if [ -f ".env" ]; then
        # Source the .env file to get database variables
        set -a
        source .env
        set +a
        
        # Try to create database (this might fail if already exists)
        print_status "Creating database '$DB_NAME'..."
        sudo -u postgres createdb $DB_NAME 2>/dev/null || print_warning "Database might already exist"
        
        # Create user if doesn't exist
        print_status "Creating database user '$DB_USER'..."
        sudo -u postgres createuser $DB_USER 2>/dev/null || print_warning "User might already exist"
        
        # Set password and permissions
        sudo -u postgres psql -c "ALTER USER $DB_USER PASSWORD '$DB_PASSWORD';" 2>/dev/null || true
        sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE $DB_NAME TO $DB_USER;" 2>/dev/null || true
        sudo -u postgres psql -c "ALTER USER $DB_USER CREATEDB;" 2>/dev/null || true
        
        print_success "Database setup completed"
    else
        print_error ".env file not found. Please run the environment setup first."
        exit 1
    fi
}

# Run Django migrations
run_migrations() {
    print_status "Running Django migrations..."
    
    cd salesmgt
    source ../venv/bin/activate
    
    # Make migrations
    python manage.py makemigrations
    
    # Apply migrations
    python manage.py migrate
    
    print_success "Migrations completed"
    
    cd ..
}

# Create superuser
create_superuser() {
    print_status "Creating Django superuser..."
    
    cd salesmgt
    source ../venv/bin/activate
    
    echo
    print_warning "Please create a superuser account for Django admin:"
    python manage.py createsuperuser
    
    print_success "Superuser created"
    
    cd ..
}

# Load initial data
load_initial_data() {
    print_status "Loading initial data..."
    
    cd salesmgt
    source ../venv/bin/activate
    
    # Check if fixtures exist
    if [ -f "sales/fixtures/initial_data.json" ]; then
        python manage.py loaddata sales/fixtures/initial_data.json
        print_success "Initial data loaded"
    else
        print_warning "No initial data fixtures found"
    fi
    
    cd ..
}

# Run tests
run_tests() {
    print_status "Running tests..."
    
    cd salesmgt
    source ../venv/bin/activate
    
    python manage.py test
    
    print_success "All tests passed"
    
    cd ..
}

# Main installation process
main() {
    echo "Starting installation process..."
    echo
    
    # Check prerequisites
    check_python
    check_postgresql
    
    # Setup environment
    create_venv
    install_dependencies
    setup_env
    
    # Ask user about database setup
    echo
    read -p "Do you want to set up the database automatically? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_database
        run_migrations
        
        # Ask about superuser
        echo
        read -p "Do you want to create a superuser now? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            create_superuser
        fi
        
        # Ask about initial data
        echo
        read -p "Do you want to load initial sample data? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            load_initial_data
        fi
    else
        print_warning "Database setup skipped. Please configure manually."
    fi
    
    # Ask about running tests
    echo
    read -p "Do you want to run tests to verify installation? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        run_tests
    fi
    
    # Installation complete
    echo
    echo "🎉 Installation completed successfully!"
    echo
    print_success "Next steps:"
    echo "  1. Update .env file with your database configuration (if not done)"
    echo "  2. Navigate to the project: cd salesmgt"
    echo "  3. Activate virtual environment: source ../venv/bin/activate"
    echo "  4. Start development server: python manage.py runserver"
    echo "  5. Open browser to: http://127.0.0.1:8000/"
    echo "  6. Access admin panel: http://127.0.0.1:8000/admin/"
    echo
    print_status "For more information, check the README.md file"
}

# Handle script interruption
trap 'echo; print_error "Installation interrupted by user"; exit 1' INT

# Check if script is being run from the correct directory
if [ ! -f "requirements.txt" ]; then
    print_error "This script must be run from the project root directory"
    print_error "Make sure you're in the sales-management directory"
    exit 1
fi

# Run main installation
main

exit 0