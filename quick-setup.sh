#!/bin/bash

# Quick Setup Script for Sales Management System
# This script helps you get started quickly with Docker

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

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

# Header
echo "🚀 Sales Management System - Quick Setup"
echo "========================================"
echo

# Check if we're in the right directory
if [ ! -f "docker-compose.yml" ]; then
    print_error "Please run this script from the project root directory"
    print_error "Expected files: docker-compose.yml, requirements.txt"
    exit 1
fi

# Make scripts executable
print_status "Making scripts executable..."
chmod +x scripts/*.sh
print_success "Scripts are now executable"

# Check Docker installation
print_status "Checking Docker installation..."
if ! command -v docker &> /dev/null; then
    print_error "Docker is not installed!"
    print_warning "Please install Docker first:"
    echo "  - Ubuntu: curl -fsSL https://get.docker.com | sh"
    echo "  - macOS: Download Docker Desktop"
    echo "  - Windows: Download Docker Desktop"
    exit 1
fi

if ! command -v docker-compose &> /dev/null; then
    print_error "Docker Compose is not installed!"
    print_warning "Please install Docker Compose first"
    exit 1
fi

print_success "Docker and Docker Compose are installed"

# Create environment file if it doesn't exist
print_status "Setting up environment configuration..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    
    # Generate secret key if Python is available
    if command -v python3 &> /dev/null; then
        SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())" 2>/dev/null || echo "your-secret-key-here")
        sed -i "s/your-secret-key-here-replace-with-actual-secret-key/$SECRET_KEY/" .env
        print_success "Generated new secret key"
    fi
    
    print_success "Environment file created (.env)"
else
    print_warning "Environment file already exists"
fi

# Ask user what they want to do
echo
echo "What would you like to do?"
echo "1. Test locally with Docker (RECOMMENDED)"
echo "2. Prepare for DigitalOcean deployment"
echo "3. View setup documentation"
echo "4. Exit"
echo

read -p "Choose an option (1-4): " choice

case $choice in
    1)
        print_status "Starting local Docker environment..."
        print_warning "This will:"
        echo "  - Build Docker images"
        echo "  - Start PostgreSQL, Redis, Django, and Nginx"
        echo "  - Run database migrations"
        echo "  - Optionally create superuser"
        echo
        
        read -p "Continue? (y/n): " -n 1 -r
        echo
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            ./scripts/local-docker.sh start
        else
            print_warning "Local setup cancelled"
        fi
        ;;
    
    2)
        print_status "Preparing for DigitalOcean deployment..."
        
        # Create production environment file
        if [ ! -f ".env.prod" ]; then
            cp .env.prod.example .env.prod
            
            # Generate secret key
            if command -v python3 &> /dev/null; then
                SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))" 2>/dev/null || echo "change-this-secret-key")
                sed -i "s/your-super-secret-production-key-change-this/$SECRET_KEY/" .env.prod
            fi
            
            print_success "Created .env.prod file"
        else
            print_warning ".env.prod already exists"
        fi
        
        print_warning "IMPORTANT: Please edit .env.prod and update:"
        echo "  - ALLOWED_HOSTS with your domain/IP"
        echo "  - DB_PASSWORD with a secure password"
        echo "  - Email settings if needed"
        echo
        print_status "Next steps:"
        echo "1. Create DigitalOcean droplet (Ubuntu 22.04, \$4/month)"
        echo "2. SSH into your droplet"
        echo "3. Run: curl -sSL https://raw.githubusercontent.com/mburuxx/sales-management/main/scripts/deploy-digitalocean.sh | bash"
        echo
        ;;
    
    3)
        print_status "Opening documentation..."
        if command -v less &> /dev/null; then
            less NEXT-STEPS.md
        elif command -v more &> /dev/null; then
            more NEXT-STEPS.md
        else
            cat NEXT-STEPS.md
        fi
        ;;
    
    4)
        print_status "Goodbye!"
        exit 0
        ;;
    
    *)
        print_error "Invalid option. Please choose 1-4."
        exit 1
        ;;
esac

echo
print_success "Setup completed! 🎉"
echo
print_status "Useful commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop app: docker-compose down"
echo "  - Restart: docker-compose restart"
echo "  - Django shell: docker-compose exec web python manage.py shell"
echo
print_status "For detailed documentation, see: NEXT-STEPS.md"