#!/bin/bash

# DigitalOcean Deployment Script for Sales Management System
# This script sets up the application on a fresh Ubuntu 20.04+ droplet

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

# Check if running as root
check_root() {
    if [ "$EUID" -eq 0 ]; then
        print_error "Please do not run this script as root. Use a regular user with sudo privileges."
        exit 1
    fi
}

# Update system
update_system() {
    print_status "Updating system packages..."
    sudo apt update && sudo apt upgrade -y
    print_success "System updated"
}

# Install Docker
install_docker() {
    print_status "Installing Docker..."
    
    # Remove old versions
    sudo apt remove -y docker docker-engine docker.io containerd runc 2>/dev/null || true
    
    # Install dependencies
    sudo apt install -y apt-transport-https ca-certificates curl gnupg lsb-release
    
    # Add Docker GPG key
    curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
    
    # Add Docker repository
    echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
    
    # Install Docker
    sudo apt update
    sudo apt install -y docker-ce docker-ce-cli containerd.io
    
    # Add user to docker group
    sudo usermod -aG docker $USER
    
    print_success "Docker installed"
}

# Install Docker Compose
install_docker_compose() {
    print_status "Installing Docker Compose..."
    
    # Get latest version
    DOCKER_COMPOSE_VERSION=$(curl -s https://api.github.com/repos/docker/compose/releases/latest | grep '"tag_name"' | cut -d'"' -f4)
    
    # Download and install
    sudo curl -L "https://github.com/docker/compose/releases/download/${DOCKER_COMPOSE_VERSION}/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
    
    print_success "Docker Compose installed"
}

# Setup firewall
setup_firewall() {
    print_status "Configuring firewall..."
    
    sudo ufw --force reset
    sudo ufw default deny incoming
    sudo ufw default allow outgoing
    sudo ufw allow ssh
    sudo ufw allow 80/tcp
    sudo ufw allow 443/tcp
    sudo ufw --force enable
    
    print_success "Firewall configured"
}

# Clone repository
clone_repository() {
    print_status "Cloning repository..."
    
    if [ -d "sales-management" ]; then
        print_warning "Repository already exists. Updating..."
        cd sales-management
        git pull origin main
    else
        git clone https://github.com/mburuxx/sales-management.git
        cd sales-management
    fi
    
    print_success "Repository ready"
}

# Setup environment
setup_environment() {
    print_status "Setting up environment..."
    
    # Copy production environment template
    if [ ! -f ".env.prod" ]; then
        cp .env.prod.example .env.prod
        
        # Generate secret key
        SECRET_KEY=$(python3 -c "import secrets; print(secrets.token_urlsafe(50))")
        sed -i "s/your-super-secret-production-key-change-this/$SECRET_KEY/" .env.prod
        
        # Get server IP
        SERVER_IP=$(curl -s https://ipinfo.io/ip)
        sed -i "s/your-droplet-ip/$SERVER_IP/" .env.prod
        
        print_warning "Please edit .env.prod file and update:"
        print_warning "  - ALLOWED_HOSTS with your domain name"
        print_warning "  - DB_PASSWORD with a secure password"
        print_warning "  - Email settings if needed"
        
        read -p "Press Enter to continue after updating .env.prod file..."
    else
        print_warning ".env.prod already exists"
    fi
    
    print_success "Environment setup complete"
}

# Deploy application
deploy_application() {
    print_status "Deploying application..."
    
    # Build and start containers
    newgrp docker << COMMANDS
    docker-compose -f docker-compose.prod.yml build
    docker-compose -f docker-compose.prod.yml up -d
COMMANDS
    
    print_success "Application deployed"
}

# Run migrations
run_migrations() {
    print_status "Running database migrations..."
    
    # Wait for database to be ready
    sleep 30
    
    newgrp docker << COMMANDS
    docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate
COMMANDS
    
    print_success "Migrations completed"
}

# Create superuser
create_superuser() {
    print_status "Creating superuser..."
    
    print_warning "You'll need to create a superuser account:"
    newgrp docker << COMMANDS
    docker-compose -f docker-compose.prod.yml exec web python manage.py createsuperuser
COMMANDS
    
    print_success "Superuser created"
}

# Setup SSL (optional)
setup_ssl() {
    read -p "Do you want to set up SSL with Let's Encrypt? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        print_status "Setting up SSL..."
        
        # Install certbot
        sudo apt install -y certbot python3-certbot-nginx
        
        read -p "Enter your domain name: " DOMAIN_NAME
        read -p "Enter your email address: " EMAIL_ADDRESS
        
        # Get SSL certificate
        sudo certbot --nginx -d $DOMAIN_NAME -d www.$DOMAIN_NAME --email $EMAIL_ADDRESS --agree-tos --non-interactive
        
        # Update nginx configuration for SSL
        # This would require updating the nginx config to enable HTTPS server block
        
        print_success "SSL setup complete"
    fi
}

# Setup monitoring
setup_monitoring() {
    print_status "Setting up basic monitoring..."
    
    # Create monitoring script
    cat > monitor.sh << 'EOF'
#!/bin/bash
# Basic monitoring script

LOG_FILE="/var/log/sales-management-monitor.log"

check_containers() {
    echo "[$(date)] Checking container status..." >> $LOG_FILE
    
    if ! docker-compose -f docker-compose.prod.yml ps | grep -q "Up"; then
        echo "[$(date)] Some containers are down. Attempting restart..." >> $LOG_FILE
        docker-compose -f docker-compose.prod.yml up -d
    fi
}

check_disk_space() {
    DISK_USAGE=$(df / | grep -vE '^Filesystem' | awk '{print $5}' | sed 's/%//')
    if [ $DISK_USAGE -gt 85 ]; then
        echo "[$(date)] WARNING: Disk usage is ${DISK_USAGE}%" >> $LOG_FILE
    fi
}

check_containers
check_disk_space
EOF

    chmod +x monitor.sh
    
    # Add to crontab
    (crontab -l 2>/dev/null; echo "*/5 * * * * /home/$USER/sales-management/monitor.sh") | crontab -
    
    print_success "Basic monitoring setup complete"
}

# Main deployment function
main() {
    echo "🚀 DigitalOcean Deployment for Sales Management System"
    echo "=================================================="
    echo
    
    check_root
    update_system
    install_docker
    install_docker_compose
    setup_firewall
    clone_repository
    setup_environment
    deploy_application
    run_migrations
    
    # Ask for optional steps
    echo
    read -p "Do you want to create a superuser now? (y/n): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        create_superuser
    fi
    
    setup_ssl
    setup_monitoring
    
    # Final information
    echo
    echo "🎉 Deployment completed successfully!"
    echo
    print_success "Your application is now running at:"
    SERVER_IP=$(curl -s https://ipinfo.io/ip)
    echo "  - HTTP: http://$SERVER_IP"
    echo "  - Admin: http://$SERVER_IP/admin/"
    echo
    print_status "Next steps:"
    echo "  1. Update your domain DNS to point to $SERVER_IP"
    echo "  2. Update ALLOWED_HOSTS in .env.prod with your domain"
    echo "  3. Restart containers: docker-compose -f docker-compose.prod.yml restart"
    echo "  4. Set up regular backups"
    echo
    print_warning "Important files:"
    echo "  - Application logs: docker-compose -f docker-compose.prod.yml logs"
    echo "  - Environment config: .env.prod"
    echo "  - Monitor script: ./monitor.sh"
}

# Run main function
main "$@"