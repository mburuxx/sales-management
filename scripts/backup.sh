#!/bin/bash

# Backup Script for Sales Management System
# This script creates backups of the database and media files

set -e

# Configuration
BACKUP_DIR="/home/$USER/backups/sales-management"
DATE=$(date +%Y%m%d_%H%M%S)
RETENTION_DAYS=7

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

# Create backup directory
create_backup_dir() {
    mkdir -p "$BACKUP_DIR"
    print_status "Backup directory: $BACKUP_DIR"
}

# Backup database
backup_database() {
    print_status "Backing up database..."
    
    DB_BACKUP_FILE="$BACKUP_DIR/database_backup_$DATE.sql"
    
    # Get database credentials from environment
    if [ -f ".env.prod" ]; then
        source .env.prod
    elif [ -f ".env" ]; then
        source .env
    else
        print_error "No environment file found"
        exit 1
    fi
    
    # Create database backup
    docker-compose exec -T db pg_dump -U "$DB_USER" "$DB_NAME" > "$DB_BACKUP_FILE"
    
    if [ $? -eq 0 ]; then
        print_success "Database backup created: $DB_BACKUP_FILE"
        
        # Compress backup
        gzip "$DB_BACKUP_FILE"
        print_success "Database backup compressed: ${DB_BACKUP_FILE}.gz"
    else
        print_error "Database backup failed"
        exit 1
    fi
}

# Backup media files
backup_media() {
    print_status "Backing up media files..."
    
    MEDIA_BACKUP_FILE="$BACKUP_DIR/media_backup_$DATE.tar.gz"
    
    # Check if media volume exists
    if docker volume ls | grep -q "sales-management_media_volume"; then
        # Create media backup from Docker volume
        docker run --rm \
            -v sales-management_media_volume:/source:ro \
            -v "$BACKUP_DIR":/backup \
            alpine \
            tar -czf "/backup/media_backup_$DATE.tar.gz" -C /source .
        
        if [ $? -eq 0 ]; then
            print_success "Media backup created: $MEDIA_BACKUP_FILE"
        else
            print_error "Media backup failed"
            exit 1
        fi
    else
        print_warning "No media volume found, skipping media backup"
    fi
}

# Backup static files
backup_static() {
    print_status "Backing up static files..."
    
    STATIC_BACKUP_FILE="$BACKUP_DIR/static_backup_$DATE.tar.gz"
    
    # Check if static volume exists
    if docker volume ls | grep -q "sales-management_static_volume"; then
        # Create static backup from Docker volume
        docker run --rm \
            -v sales-management_static_volume:/source:ro \
            -v "$BACKUP_DIR":/backup \
            alpine \
            tar -czf "/backup/static_backup_$DATE.tar.gz" -C /source .
        
        if [ $? -eq 0 ]; then
            print_success "Static files backup created: $STATIC_BACKUP_FILE"
        else
            print_warning "Static files backup failed"
        fi
    else
        print_warning "No static volume found, skipping static backup"
    fi
}

# Backup configuration files
backup_config() {
    print_status "Backing up configuration files..."
    
    CONFIG_BACKUP_FILE="$BACKUP_DIR/config_backup_$DATE.tar.gz"
    
    # Create config backup
    tar -czf "$CONFIG_BACKUP_FILE" \
        .env* \
        docker-compose*.yml \
        nginx/ \
        scripts/ \
        2>/dev/null || true
    
    if [ $? -eq 0 ]; then
        print_success "Configuration backup created: $CONFIG_BACKUP_FILE"
    else
        print_warning "Configuration backup failed"
    fi
}

# Clean old backups
cleanup_old_backups() {
    print_status "Cleaning up old backups (older than $RETENTION_DAYS days)..."
    
    find "$BACKUP_DIR" -name "*backup_*" -mtime +$RETENTION_DAYS -delete
    
    print_success "Old backups cleaned up"
}

# Upload to remote storage (optional)
upload_to_remote() {
    if [ ! -z "$BACKUP_REMOTE_PATH" ]; then
        print_status "Uploading backups to remote storage..."
        
        # Example for AWS S3 (uncomment if using)
        # aws s3 sync "$BACKUP_DIR" "$BACKUP_REMOTE_PATH" --delete
        
        # Example for rsync to remote server (uncomment if using)
        # rsync -avz --delete "$BACKUP_DIR/" "$BACKUP_REMOTE_PATH/"
        
        print_warning "Remote upload not configured. Set BACKUP_REMOTE_PATH to enable."
    fi
}

# Restore database from backup
restore_database() {
    if [ -z "$1" ]; then
        print_error "Please provide backup file path"
        echo "Usage: $0 restore-db /path/to/backup.sql.gz"
        exit 1
    fi
    
    BACKUP_FILE="$1"
    
    if [ ! -f "$BACKUP_FILE" ]; then
        print_error "Backup file not found: $BACKUP_FILE"
        exit 1
    fi
    
    print_warning "This will overwrite the current database. Are you sure?"
    read -p "Type 'yes' to continue: " confirmation
    
    if [ "$confirmation" != "yes" ]; then
        print_error "Database restore cancelled"
        exit 1
    fi
    
    print_status "Restoring database from $BACKUP_FILE..."
    
    # Get database credentials
    if [ -f ".env.prod" ]; then
        source .env.prod
    elif [ -f ".env" ]; then
        source .env
    fi
    
    # Restore database
    if [[ "$BACKUP_FILE" == *.gz ]]; then
        gunzip -c "$BACKUP_FILE" | docker-compose exec -T db psql -U "$DB_USER" "$DB_NAME"
    else
        docker-compose exec -T db psql -U "$DB_USER" "$DB_NAME" < "$BACKUP_FILE"
    fi
    
    if [ $? -eq 0 ]; then
        print_success "Database restored successfully"
    else
        print_error "Database restore failed"
        exit 1
    fi
}

# List available backups
list_backups() {
    print_status "Available backups in $BACKUP_DIR:"
    
    if [ -d "$BACKUP_DIR" ]; then
        ls -lh "$BACKUP_DIR" | grep backup_
    else
        print_warning "No backup directory found"
    fi
}

# Show backup info
show_backup_info() {
    echo "Backup Configuration:"
    echo "  - Backup directory: $BACKUP_DIR"
    echo "  - Retention period: $RETENTION_DAYS days"
    echo "  - Current date: $DATE"
    
    if [ -d "$BACKUP_DIR" ]; then
        BACKUP_COUNT=$(ls "$BACKUP_DIR" | grep backup_ | wc -l)
        BACKUP_SIZE=$(du -sh "$BACKUP_DIR" | cut -f1)
        echo "  - Existing backups: $BACKUP_COUNT"
        echo "  - Total backup size: $BACKUP_SIZE"
    fi
}

# Main function
main() {
    case "${1:-backup}" in
        backup|full-backup)
            create_backup_dir
            backup_database
            backup_media
            backup_static
            backup_config
            cleanup_old_backups
            upload_to_remote
            print_success "Full backup completed successfully"
            ;;
        db-backup)
            create_backup_dir
            backup_database
            cleanup_old_backups
            print_success "Database backup completed"
            ;;
        media-backup)
            create_backup_dir
            backup_media
            print_success "Media backup completed"
            ;;
        restore-db)
            restore_database "$2"
            ;;
        list)
            list_backups
            ;;
        info)
            show_backup_info
            ;;
        help|--help|-h)
            echo "Usage: $0 [OPTION] [FILE]"
            echo
            echo "Options:"
            echo "  backup        Create full backup (default)"
            echo "  db-backup     Backup only database"
            echo "  media-backup  Backup only media files"
            echo "  restore-db    Restore database from backup file"
            echo "  list          List available backups"
            echo "  info          Show backup configuration"
            echo "  help          Show this help message"
            echo
            echo "Examples:"
            echo "  $0 backup                              # Create full backup"
            echo "  $0 restore-db /path/to/backup.sql.gz  # Restore database"
            echo "  $0 list                                # List backups"
            ;;
        *)
            print_error "Unknown option: $1"
            echo "Use '$0 help' for usage information"
            exit 1
            ;;
    esac
}

# Run main function
main "$@"