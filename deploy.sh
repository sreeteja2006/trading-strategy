#!/bin/bash
# Quick deployment script for global website access

echo "🚀 Starting global deployment..."

# Stop any existing containers
echo "Stopping existing containers..."
docker-compose down 2>/dev/null || true

# Build and start the application
echo "Building and starting the application..."
docker-compose up --build -d

# Wait for the application to start
echo "Waiting for application to start..."
sleep 10

# Check if the application is running
if curl -f http://localhost/api/system_status >/dev/null 2>&1; then
    echo "✅ Application is running successfully!"
    echo "🌐 Access your trading system at: http://localhost"
    echo "🔄 Application will restart automatically if it crashes"
    
    # Show container status
    echo ""
    echo "📊 Container Status:"
    docker-compose ps
    
    echo ""
    echo "📝 To view logs: docker-compose logs -f"
    echo "🛑 To stop: docker-compose down"
    
else
    echo "❌ Application failed to start. Checking logs..."
    docker-compose logs
    exit 1
fi