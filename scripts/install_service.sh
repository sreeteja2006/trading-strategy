#!/bin/bash

# Install the Trading Strategy System as a systemd service
# This script sets up the system to run 24/7 on Arch Linux

echo "Installing Trading Strategy System as a systemd service..."
echo "========================================================="

# Check if running as root
if [ "$EUID" -ne 0 ]; then
  echo "Please run as root or with sudo"
  exit 1
fi

# Get the absolute path to the project directory
PROJECT_DIR=$(cd "$(dirname "$0")/.." && pwd)

# Update the service file with the correct path
sed "s|/path/to/trading-strategy-system|$PROJECT_DIR|g" "$PROJECT_DIR/scripts/trading-system.service" > /etc/systemd/system/trading-system.service

# Reload systemd to recognize the new service
systemctl daemon-reload

echo "Service installed successfully!"
echo ""
echo "To enable the service to start on boot:"
echo "  sudo systemctl enable trading-system.service"
echo ""
echo "To start the service now:"
echo "  sudo systemctl start trading-system.service"
echo ""
echo "To check the status:"
echo "  sudo systemctl status trading-system.service"
echo ""
echo "To view logs:"
echo "  sudo journalctl -u trading-system.service"