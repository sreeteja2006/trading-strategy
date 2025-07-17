#!/bin/bash
# Check global access to your trading system

echo "🌐 Trading System Access Information"
echo "=================================="

# Get local IP
LOCAL_IP=$(ip route get 1 | awk '{print $7}' | head -1 2>/dev/null || echo "localhost")

# Get public IP (IPv4 only)
PUBLIC_IP=$(curl -s ipv4.icanhazip.com 2>/dev/null || curl -s ifconfig.me 2>/dev/null || echo "Unable to detect")

echo ""
echo "🔗 Access URLs:"
echo "   Local Access:    http://localhost"
echo "   Network Access:  http://$LOCAL_IP"
echo "   Global Access:   http://$PUBLIC_IP"
echo ""

# Check if the service is running
if curl -f http://localhost/api/system_status >/dev/null 2>&1; then
    echo "✅ Trading System Status: ONLINE"
    echo ""
    echo "📱 Available Pages:"
    echo "   🏠 Home Page:           http://localhost"
    echo "   📈 Trading Dashboard:   http://localhost/dashboard"
    echo "   💰 Performance:        http://localhost/performance"
    echo "   🚀 Trading Interface:  http://localhost/trading"
    echo ""
    echo "🔧 Management:"
    echo "   View Logs:    docker-compose logs -f"
    echo "   Restart:      docker-compose restart"
    echo "   Stop:         docker-compose down"
    echo ""
    echo "🌍 For Global Access:"
    echo "   1. Make sure port 80 is open on your router/firewall"
    echo "   2. Share this URL: http://$PUBLIC_IP"
    echo "   3. Anyone can access your trading system globally!"
else
    echo "❌ Trading System Status: OFFLINE"
    echo "Run: ./start_global.sh to start the system"
fi