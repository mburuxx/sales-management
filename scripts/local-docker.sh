#!/bin/bash

# Local Development with Docker Script
# This script helps you run the application locally with Docker

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

# Check if Docker is installed
check_docker() {
    if ! command -v docker &> /dev/null; then
        print_error "Docker is not installed. Please install Docker first."
        exit 1
    fi
    
    if ! command -v docker-compose &> /dev/null; then
        print_error "Docker Compose is not installed. Please install Docker Compose first."
        exit 1
    fi
    
    print_success "Docker and Docker Compose are installed"
}

# Setup environment
setup_environment() {
    print_status "Setting up development environment..."
    
    if [ ! -f ".env" ]; then
        cp .env.example .env
        
        # Generate secret key
        if command -v python3 &> /dev/null; then
            SECRET_KEY=$(python3 -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
            sed -i "s/your-secret-key-here-replace-with-actual-secret-key/$SECRET_KEY/" .env
        fi
        
        print_success "Environment file created"
    else
        print_warning "Environment file already exists"
    fi
}

# Build and start containers
start_containers() {
    print_status "Building and starting containers..."
    
    # Build images
    docker-compose build
    
    # Start containers
    docker-compose up -d
    
    print_success "Containers started"
}

# Wait for database
wait_for_database() {
    print_status "Waiting for database to be ready..."
    
    # Wait for database container to be healthy
    timeout=60
    while [ $timeout -gt 0 ]; do
        if docker-compose exec db pg_isready -U postgres > /dev/null 2>&1; then
            print_success "Database is ready"
            return 0
        fi
        sleep 2
        timeout=$((timeout - 2))
    done
    
    print_error "Database failed to start within 60 seconds"
    exit 1
}

# Run migrations
run_migrations() {
    print_status "Running database migrations..."
    
    docker-compose exec web python manage.py makemigrations
    docker-compose exec web python manage.py migrate
    
    print_success "Migrations completed"
}

# Create superuser
create_superuser() {
    print_status "Creating superuser..."
    
    docker-compose exec web python manage.py createsuperuser
    
    print_success "Superuser created"
}

# Load sample data
load_sample_data() {
    print_status "Loading sample data..."
    
    if docker-compose exec web test -f sales/fixtures/initial_data.json; then
        docker-compose exec web python manage.py loaddata sales/fixtures/initial_data.json
        print_success "Sample data loaded"
    else
        print_warning "No sample data found"
    fi
}

# Show application status
show_status() {
    print_status "Application status:"
    docker-compose ps
    
    echo
    print_success "Application URLs:"
    echo "  - Main application: http://localhost:8000"
    echo "  - Admin interface: http://localhost:8000/admin/"
    echo "  - Database: localhost:5432"
    echo "  - Redis: localhost:6379"
    
    echo
    print_status "Useful commands:"
    echo "  - View logs: docker-compose logs -f"
    echo "  - Stop application: docker-compose down"
    echo "  - Restart application: docker-compose restart"
    echo "  - Run Django commands: docker-compose exec web python manage.py <command>"
}

# Stop containers
stop_containers() {
    print_status "Stopping containers..."
    docker-compose down
    print_success "Containers stopped"
}

# Clean up
cleanup() {
    print_status "Cleaning up..."
    docker-compose down -v --remove-orphans
    docker system prune -f
    print_success "Cleanup completed"
}

# Show help
show_help() {
    echo "Usage: $0 [OPTION]"
    echo
    echo "Options:"
    echo "  start     Start the application (default)"
    echo "  stop      Stop the application"
    echo "  restart   Restart the application"
    echo "  status    Show application status"
    echo "  logs      Show application logs"
    echo "  shell     Open Django shell"
    echo "  migrate   Run database migrations"
    echo "  cleanup   Clean up containers and volumes"
    echo "  help      Show this help message"
    echo
}

# Main function
main() {
    case "${1:-start}" in
        start)
            check_docker
            setup_environment
            start_containers
            wait_for_database
            run_migrations
            
            # Ask about superuser
            echo
            read -p "Do you want to create a superuser? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                create_superuser
            fi
            
            # Ask about sample data
            echo
            read -p "Do you want to load sample data? (y/n): " -n 1 -r
            echo
            if [[ $REPLY =~ ^[Yy]$ ]]; then
                load_sample_data
            fi
            
            show_status
            ;;
        stop)
            stop_containers
            ;;
        restart)
            print_status "Restarting application..."
            docker-compose restart
            show_status
            ;;
        status)
            show_status
            ;;
        logs)
            docker-compose logs -f
            ;;
        shell)
            docker-compose exec web python manage.py shell
            ;;
        migrate)
            run_migrations
            ;;
        cleanup)
            cleanup
            ;;
        help|--help|-h)
            show_help
            ;;
        *)
            print_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"