#!/bin/bash
# Start the trading system for global access

echo "🌐 Starting Trading System for Global Access..."

# Check if port 80 is available
if lsof -Pi :80 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "⚠️  Port 80 is already in use. Stopping conflicting services..."
    sudo fuser -k 80/tcp 2>/dev/null || true
    sleep 2
fi

# Ensure Docker is running
if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Create necessary directories
mkdir -p data/processed data/raw data/results logs reports

# Set proper permissions
chmod -R 755 data logs reports scripts

# Get the server's IP address
SERVER_IP=$(ip route get 1 | awk '{print $7}' | head -1 2>/dev/null || echo "localhost")

# Get public IP (IPv4 only)
PUBLIC_IP=$(curl -s ipv4.icanhazip.com 2>/dev/null || curl -s ifconfig.me 2>/dev/null || echo "Unable to detect")

# Start the application
docker-compose up -d

echo ""
echo "✅ Trading System is now running globally!"
echo ""
echo "🔗 Access URLs:"
echo "   Local:    http://localhost"
echo "   Network:  http://$SERVER_IP"
echo "   Global:   http://$PUBLIC_IP"
echo ""
echo "📊 The system will:"
echo "   ✓ Run 24/7 automatically"
echo "   ✓ Restart if it crashes"
echo "   ✓ Monitor system health"
echo "   ✓ Handle all trading operations"
echo ""
echo "🛠️  Management commands:"
echo "   View logs:    docker-compose logs -f"
echo "   Stop system:  docker-compose down"
echo "   Restart:      docker-compose restart"
echo ""

# Start monitoring in background
nohup bash -c '
while true; do
    if ! curl -f http://localhost/api/system_status >/dev/null 2>&1; then
        echo "$(date): System unhealthy, restarting..." >> logs/monitor.log
        docker-compose restart
    fi
    sleep 60
done
' > logs/monitor.log 2>&1 &

echo "🔄 Health monitoring started in background"
echo "📝 Monitor logs: tail -f logs/monitor.log"