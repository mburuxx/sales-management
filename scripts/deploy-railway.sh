#!/bin/bash

# Railway Deployment Script for Sales Management System
# This script helps deploy your Django application to Railway

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# Check if Railway CLI is installed
check_railway_cli() {
    print_status "Checking Railway CLI installation..."
    if ! command -v railway &> /dev/null; then
        print_error "Railway CLI not found!"
        echo
        echo "To install Railway CLI:"
        echo "  npm install -g @railway/cli"
        echo "  OR"
        echo "  curl -fsSL https://railway.app/install.sh | sh"
        echo
        exit 1
    fi
    print_success "Railway CLI found"
}

# Login to Railway
railway_login() {
    print_status "Checking Railway authentication..."
    if ! railway whoami &> /dev/null; then
        print_warning "Not logged in to Railway"
        print_status "Opening Railway login..."
        railway login
    else
        print_success "Already logged in to Railway"
    fi
}

# Create Railway project
create_railway_project() {
    print_status "Setting up Railway project..."
    
    echo "Choose deployment method:"
    echo "1. Deploy from current directory"
    echo "2. Connect GitHub repository"
    read -p "Enter choice (1-2): " choice
    
    case $choice in
        1)
            print_status "Creating Railway project from current directory..."
            railway init
            ;;
        2)
            print_status "Please connect your GitHub repository manually:"
            echo "1. Go to https://railway.app/new"
            echo "2. Click 'Deploy from GitHub repo'"
            echo "3. Select your sales-management repository"
            echo "4. Configure environment variables as shown below"
            echo
            read -p "Press Enter when you've connected your GitHub repo..."
            ;;
        *)
            print_error "Invalid choice"
            exit 1
            ;;
    esac
}

# Set environment variables
set_environment_variables() {
    print_status "Setting up environment variables..."
    
    echo
    echo "Setting required environment variables:"
    
    # Generate secret key
    SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
    
    print_status "Setting SECRET_KEY..."
    railway variables set SECRET_KEY="$SECRET_KEY"
    
    print_status "Setting DEBUG to False..."
    railway variables set DEBUG=False
    
    print_status "Setting ALLOWED_HOSTS..."
    railway variables set ALLOWED_HOSTS="localhost,127.0.0.1,.railway.app"
    
    print_success "Environment variables set!"
    
    echo
    print_warning "Railway will automatically provide DATABASE_URL for PostgreSQL"
    print_warning "Make sure to add a PostgreSQL database in your Railway dashboard"
}

# Add PostgreSQL database
add_postgresql() {
    print_status "Adding PostgreSQL database..."
    
    echo
    echo "To add PostgreSQL database:"
    echo "1. Go to your Railway project dashboard"
    echo "2. Click '+ New' -> 'Database' -> 'Add PostgreSQL'"
    echo "3. Railway will automatically set DATABASE_URL environment variable"
    echo
    
    read -p "Press Enter when you've added PostgreSQL database..."
    print_success "PostgreSQL database should now be available"
}

# Deploy application
deploy_application() {
    print_status "Deploying application to Railway..."
    
    echo
    echo "Your application will be deployed with:"
    echo "- Python 3.11"
    echo "- Automatic migrations"
    echo "- Static file collection"
    echo "- Gunicorn WSGI server"
    echo
    
    print_status "Starting deployment..."
    railway up
    
    print_success "Deployment initiated!"
}

# Create superuser
create_superuser() {
    print_status "Creating superuser account..."
    
    echo
    print_warning "You'll need to create a superuser account"
    echo "Run this command after deployment:"
    echo "  railway run python manage.py createsuperuser"
    echo
    
    read -p "Do you want to create superuser now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        railway run python manage.py createsuperuser
        print_success "Superuser created!"
    else
        print_warning "Remember to create superuser later"
    fi
}

# Load initial data
load_initial_data() {
    print_status "Loading initial data..."
    
    read -p "Do you want to load sample data? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        railway run python manage.py loaddata sales/fixtures/initial_data.json
        print_success "Initial data loaded!"
    else
        print_warning "Skipping initial data loading"
    fi
}

# Show deployment info
show_deployment_info() {
    print_success "Deployment completed!"
    echo
    echo "🎉 Your Sales Management System is now deployed on Railway!"
    echo
    echo "Next steps:"
    echo "1. Check your Railway dashboard for the deployment URL"
    echo "2. Access your application at the provided URL"
    echo "3. Login with your superuser account"
    echo "4. Configure any additional settings in Django admin"
    echo
    echo "Useful Railway commands:"
    echo "  railway logs         - View application logs"
    echo "  railway variables    - View environment variables"
    echo "  railway open         - Open your deployed app"
    echo "  railway shell        - Open shell in deployed environment"
    echo
    print_status "For support, check the Railway documentation: https://docs.railway.app"
}

# Main deployment process
main() {
    echo "🚂 Railway Deployment Script"
    echo "Sales Management System"
    echo
    
    # Checks
    check_railway_cli
    railway_login
    
    # Project setup
    create_railway_project
    set_environment_variables
    add_postgresql
    
    # Deploy
    deploy_application
    
    # Post-deployment
    sleep 10  # Wait for deployment to complete
    create_superuser
    load_initial_data
    
    # Completion
    show_deployment_info
}

# Handle script interruption
trap 'echo; print_error "Deployment interrupted by user"; exit 1' INT

# Check if script is being run from the correct directory
if [ ! -f "railway.toml" ]; then
    print_error "This script must be run from the project root directory"
    print_error "Make sure you're in the sales-management directory"
    exit 1
fi

# Run main deployment
main

exit 0