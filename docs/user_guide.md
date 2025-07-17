# Trading Strategy System - User Guide

## Introduction

Welcome to the Trading Strategy System! This comprehensive platform provides tools for developing, testing, and deploying trading strategies. The system includes real-time market data visualization, backtesting capabilities, and both paper and live trading interfaces.

The system now features a 24/7 web interface that allows you to access all trading applications from a single dashboard. This interface is containerized using Docker for reliability and easy deployment, especially on Arch Linux systems.

## Getting Started

### Accessing the Web Interface

The Trading Strategy System is accessible through a web interface that runs 24/7. You can access it using any modern web browser:

1. Open your web browser
2. Navigate to: `http://your-server-ip:8501` (replace with your actual server address)
3. The home page will display with navigation to all available applications

### System Requirements

- Modern web browser (Chrome, Firefox, Safari, Edge)
- Internet connection
- Account credentials (for live trading features)

## Available Applications

### 📈 Trading Dashboard

The Trading Dashboard provides real-time market data visualization and technical indicators.

**Features:**
- Real-time price charts for selected stocks
- Technical indicators (RSI, Moving Averages)
- Volume analysis
- Market overview

**Usage:**
1. Select a stock symbol from the dropdown
2. Choose the time period for analysis
3. View the generated charts and indicators
4. Use the refresh button to update data

### 💰 Performance Dashboard

Track your trading strategy results and portfolio performance.

**Features:**
- Portfolio value tracking
- Position management
- Transaction history
- Performance metrics (win rate, Sharpe ratio, etc.)
- Portfolio allocation visualization

**Usage:**
1. View your current portfolio composition
2. Track individual position performance
3. Analyze transaction history
4. Monitor key performance metrics

### 🚀 Trading Interface

Execute trades and manage your trading strategy.

**Features:**
- Paper trading mode (virtual money)
- Live trading mode (real money)
- Strategy configuration
- Risk management settings
- Trade execution

**Usage:**
1. Select trading mode (paper/live)
2. Configure strategy parameters
3. Set risk management rules
4. Monitor trading signals
5. Execute or automate trades

### 🖥️ System Status Dashboard

Monitor the health and performance of your trading system.

**Features:**
- Real-time system resource monitoring (CPU, memory, disk)
- Docker container status and health
- Service availability checks
- System logs viewer
- Administrative actions (restart services, backup data)

**Usage:**
1. View system resource utilization
2. Check the status of all containers and services
3. Monitor system logs for issues
4. Perform administrative actions when needed
5. Set up automated monitoring with the included scripts

## Configuration

### Strategy Parameters

You can configure your trading strategy parameters in the `config/trading_config.json` file:

```json
{
  "symbols": ["RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK"],
  "max_positions": 5,
  "position_size_pct": 0.1,
  "stop_loss_pct": 0.05,
  "take_profit_pct": 0.15,
  "daily_loss_limit": 0.02,
  "max_trades_per_day": 10
}
```

### Risk Management

Risk management settings can be configured in the `config/risk_config.json` file:

```json
{
  "max_portfolio_risk": 0.02,
  "max_position_size_pct": 0.2,
  "correlation_threshold": 0.7,
  "max_sector_exposure": 0.3,
  "volatility_threshold": 0.25
}
```

## Running the System 24/7

The Trading Strategy System is designed to run continuously using Docker containers.

### Starting the System on Arch Linux

```bash
# Make sure Docker service is running
sudo systemctl start docker

# Navigate to the project directory
cd trading-strategy-system

# Start the system using the provided script
./scripts/start_website.sh

# Alternatively, start manually
docker-compose up -d
```

### Checking System Status

```bash
# Check if containers are running
docker-compose ps

# View logs
docker-compose logs -f

# Check Docker service status
systemctl status docker
```

### Stopping the System

```bash
# Stop the system
docker-compose down

# If you want to stop the Docker service as well
sudo systemctl stop docker
```

### Setting Up Automatic Start on Boot (Arch Linux)

To ensure the trading system starts automatically when your Arch Linux system boots:

```bash
# Enable Docker service to start on boot
sudo systemctl enable docker

# Create a systemd service file
sudo nano /etc/systemd/system/trading-system.service
```

Add the following content to the service file:

```
[Unit]
Description=Trading Strategy System
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
RemainAfterExit=yes
WorkingDirectory=/path/to/trading-strategy-system
ExecStart=/usr/bin/docker-compose up -d
ExecStop=/usr/bin/docker-compose down

[Install]
WantedBy=multi-user.target
```

Then enable and start the service:

```bash
sudo systemctl enable trading-system.service
sudo systemctl start trading-system.service
```

## Management Tools

The Trading Strategy System comes with several tools to help you manage the 24/7 website.

### Command-Line Management Tool

The `manage_website.py` script provides a convenient way to manage the system from the command line:

```bash
# Check system status
python scripts/manage_website.py status

# Start the system
python scripts/manage_website.py start

# Stop the system
python scripts/manage_website.py stop

# Restart the system
python scripts/manage_website.py restart

# View logs (last 50 lines by default)
python scripts/manage_website.py logs
python scripts/manage_website.py logs --lines 100

# Backup data
python scripts/manage_website.py backup

# Update the system
python scripts/manage_website.py update
```

### Automated Monitoring

The `monitor_website.sh` script automatically checks if the website is running and restarts it if needed:

```bash
# Run the monitoring script manually
./scripts/monitor_website.sh

# Set up automatic monitoring (the script will configure this for you)
# It will create a cron job to check the website every 5 minutes
```

### System Service

For a more robust solution, you can install the system as a systemd service:

```bash
# Install the service (requires root privileges)
sudo ./scripts/install_service.sh

# Enable and start the service
sudo systemctl enable trading-system.service
sudo systemctl start trading-system.service
```

## Troubleshooting

### Common Issues

1. **Web interface not accessible**
   - Check if Docker containers are running: `docker-compose ps`
   - Verify Docker service is running: `systemctl status docker`
   - Ensure port 8501 is open: `ss -tuln | grep 8501`
   - Check the system status dashboard: `http://localhost:8501/system`

2. **Data not updating**
   - Check internet connectivity
   - Verify API access
   - Refresh the page
   - Restart the specific service: `docker-compose restart trading-app`

3. **Trading errors**
   - Check account balance
   - Verify broker connectivity
   - Review error logs: `docker-compose logs trading-app`
   - Check the system status dashboard for service health

4. **Docker-related issues**
   - Clear Docker cache: `docker system prune`
   - Rebuild containers: `docker-compose build --no-cache`
   - Check Docker logs: `journalctl -u docker`

### Getting Help

If you encounter issues not covered in this guide:

1. Check the logs: `docker-compose logs -f`
2. Review the error messages in the web interface
3. Use the System Status Dashboard to diagnose issues
4. Run the monitoring script: `./scripts/monitor_website.sh`
5. Contact system administrator for assistance

## Advanced Features

### Automated Trading

The system supports automated trading based on your configured strategy:

1. Configure your strategy parameters
2. Set risk management rules
3. Enable automated trading in the Trading Interface
4. Monitor performance in real-time

### Custom Strategies

You can develop custom trading strategies by:

1. Creating new strategy modules in `src/strategy/`
2. Implementing signal generation logic
3. Registering the strategy in the system
4. Testing with backtesting before live deployment

## Security Considerations

- Always use strong passwords
- Enable two-factor authentication for broker accounts
- Regularly review transaction history
- Set appropriate risk limits
- Never share your credentials

## Updates and Maintenance

The system is designed for continuous operation, but periodic maintenance is recommended:

1. Update dependencies: `docker-compose build --pull`
2. Restart the system: `docker-compose restart`
3. Check for system updates regularly

---

Thank you for using the Trading Strategy System! This guide will be updated as new features are added.