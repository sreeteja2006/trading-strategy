#!/bin/bash

# Monitor the Trading Strategy System website
# This script checks if the website is running and restarts it if needed
# Optimized for Arch Linux

# Configuration
CHECK_INTERVAL=300  # Check every 5 minutes
MAX_RESTART_ATTEMPTS=3
LOG_FILE="/var/log/trading-system-monitor.log"
WEBHOOK_URL=""  # Optional: Add your notification webhook URL here

# Function to log messages
log_message() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1" | tee -a "$LOG_FILE"
}

# Function to send notifications
send_notification() {
    if [ -n "$WEBHOOK_URL" ]; then
        curl -s -X POST -H "Content-Type: application/json" \
            -d "{\"text\":\"Trading System Alert: $1\"}" \
            "$WEBHOOK_URL" > /dev/null
    fi
}

# Create log file if it doesn't exist
if [ ! -f "$LOG_FILE" ]; then
    touch "$LOG_FILE"
    log_message "Monitoring started"
fi

# Navigate to the project root directory
cd "$(dirname "$0")/.."
PROJECT_DIR=$(pwd)

log_message "Monitoring Trading Strategy System Website..."

# Check if Docker is running
if ! systemctl is-active --quiet docker; then
    log_message "Docker service is not running. Starting Docker service..."
    sudo systemctl start docker
    sleep 10  # Wait for Docker to start
fi

# Check if the containers are running
CONTAINER_COUNT=$(docker-compose ps -q | wc -l)
if [ "$CONTAINER_COUNT" -eq 0 ]; then
    log_message "No containers running. Starting services..."
    docker-compose up -d
    sleep 20  # Wait for containers to start
fi

# Check if the website is accessible
restart_attempts=0
while ! curl -s -f http://localhost:8501/_stcore/health > /dev/null; do
    if [ "$restart_attempts" -ge "$MAX_RESTART_ATTEMPTS" ]; then
        log_message "ERROR: Website failed to start after $MAX_RESTART_ATTEMPTS attempts"
        send_notification "Website failed to start after multiple attempts. Manual intervention required."
        exit 1
    fi
    
    log_message "Website is not accessible. Attempting restart..."
    docker-compose down
    sleep 5
    docker-compose up -d
    sleep 20  # Wait for website to start
    
    restart_attempts=$((restart_attempts + 1))
done

# If we got here, the website is running
if [ "$restart_attempts" -gt 0 ]; then
    log_message "Website restarted successfully after $restart_attempts attempts"
    send_notification "Website was down but has been successfully restarted"
else
    log_message "Website is running properly"
fi

# Get container stats
log_message "Container Stats:"
docker stats --no-stream $(docker-compose ps -q) | tee -a "$LOG_FILE"

# Set up a cron job to run this script regularly if it doesn't exist
if ! crontab -l | grep -q "monitor_website.sh"; then
    log_message "Setting up cron job to run monitoring script every $CHECK_INTERVAL seconds"
    (crontab -l 2>/dev/null; echo "*/$((CHECK_INTERVAL / 60)) * * * * $PROJECT_DIR/scripts/monitor_website.sh") | crontab -
fi

exit 0