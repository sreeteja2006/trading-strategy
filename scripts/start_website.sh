#!/bin/bash

# Start the Trading Strategy System website
# This script starts the Docker containers for the 24/7 web interface
# Optimized for Arch Linux

echo "Starting Trading Strategy System Website..."
echo "============================================"

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "Error: Docker is not installed. Please install Docker first."
    echo "Run: sudo pacman -S docker"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Error: Docker Compose is not installed. Please install Docker Compose first."
    echo "Run: sudo pacman -S docker-compose"
    exit 1
fi

# Check if Docker service is running
if ! systemctl is-active --quiet docker; then
    echo "Docker service is not running. Starting Docker service..."
    sudo systemctl start docker
fi

# Navigate to the project root directory
cd "$(dirname "$0")/.."

# Check if the docker-compose.yml file exists
if [ ! -f "docker-compose.yml" ]; then
    echo "Error: docker-compose.yml not found in the project directory."
    exit 1
fi

# Build and start the containers
echo "Building and starting containers..."
docker-compose up -d --build

# Check if the containers started successfully
if [ $? -eq 0 ]; then
    echo "Trading Strategy System Website is now running!"
    echo "Access the website at: http://localhost:8501"
    echo ""
    echo "To stop the website, run: docker-compose down"
else
    echo "Error: Failed to start the Trading Strategy System Website."
    echo "Check the logs with: docker-compose logs"
    exit 1
fi

# Display container status
echo ""
echo "Container Status:"
docker-compose ps

echo ""
echo "System is now running 24/7. Press Ctrl+C to exit this script (the website will continue running)."
echo "Monitor logs with: docker-compose logs -f"