#!/usr/bin/env python3
"""
Command-line tool to manage the Trading Strategy System website
"""
import argparse
import subprocess
import os
import sys
import time
import json
from datetime import datetime

def run_command(command, show_output=True):
    """Run a shell command and return the result"""
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=False,
            text=True,
            capture_output=True
        )
        
        if show_output:
            if result.stdout:
                print(result.stdout)
            if result.stderr:
                print(result.stderr, file=sys.stderr)
                
        return result.returncode == 0, result.stdout
    except Exception as e:
        print(f"Error executing command: {e}", file=sys.stderr)
        return False, str(e)

def get_status():
    """Get the status of the trading system"""
    print("Checking Trading Strategy System status...")
    
    # Check if Docker is running
    success, _ = run_command("systemctl is-active docker", show_output=False)
    if not success:
        print("❌ Docker service is not running")
        return False
    
    print("✅ Docker service is running")
    
    # Check if containers are running
    success, output = run_command("docker-compose ps -q", show_output=False)
    if not success or not output.strip():
        print("❌ No containers are running")
        return False
    
    print(f"✅ Containers are running")
    
    # Check if website is accessible
    success, _ = run_command("curl -s -f http://localhost:8501/_stcore/health > /dev/null", show_output=False)
    if not success:
        print("❌ Website is not accessible")
        return False
    
    print("✅ Website is accessible")
    
    # Get container details
    print("\nContainer details:")
    run_command("docker-compose ps")
    
    return True

def start_system():
    """Start the trading system"""
    print("Starting Trading Strategy System...")
    
    # Check if Docker is running
    success, _ = run_command("systemctl is-active docker", show_output=False)
    if not success:
        print("Docker service is not running. Starting Docker...")
        run_command("sudo systemctl start docker")
        time.sleep(5)  # Wait for Docker to start
    
    # Start containers
    run_command("docker-compose up -d")
    
    # Wait for containers to start
    print("Waiting for containers to start...")
    time.sleep(10)
    
    # Check status
    return get_status()

def stop_system():
    """Stop the trading system"""
    print("Stopping Trading Strategy System...")
    return run_command("docker-compose down")

def restart_system():
    """Restart the trading system"""
    print("Restarting Trading Strategy System...")
    stop_system()
    time.sleep(5)
    return start_system()

def view_logs(lines=50):
    """View system logs"""
    print(f"Showing last {lines} log lines:")
    return run_command(f"docker-compose logs --tail={lines}")

def backup_data():
    """Backup system data"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_{timestamp}.tar.gz"
    
    print(f"Creating backup: {backup_file}")
    success, _ = run_command(f"tar -czf {backup_file} data config")
    
    if success:
        print(f"✅ Backup created successfully: {backup_file}")
        file_size = os.path.getsize(backup_file) / (1024 * 1024)  # Size in MB
        print(f"   Size: {file_size:.2f} MB")
    else:
        print("❌ Backup failed")
    
    return success

def update_system():
    """Update the trading system"""
    print("Updating Trading Strategy System...")
    
    # Pull latest changes
    print("Pulling latest changes...")
    run_command("git pull")
    
    # Rebuild containers
    print("Rebuilding containers...")
    run_command("docker-compose build --pull")
    
    # Restart system
    return restart_system()

def main():
    """Main function"""
    parser = argparse.ArgumentParser(description="Manage Trading Strategy System")
    
    # Define commands
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")
    
    # Status command
    subparsers.add_parser("status", help="Check system status")
    
    # Start command
    subparsers.add_parser("start", help="Start the system")
    
    # Stop command
    subparsers.add_parser("stop", help="Stop the system")
    
    # Restart command
    subparsers.add_parser("restart", help="Restart the system")
    
    # Logs command
    logs_parser = subparsers.add_parser("logs", help="View system logs")
    logs_parser.add_argument("-n", "--lines", type=int, default=50, help="Number of log lines to show")
    
    # Backup command
    subparsers.add_parser("backup", help="Backup system data")
    
    # Update command
    subparsers.add_parser("update", help="Update the system")
    
    # Parse arguments
    args = parser.parse_args()
    
    # Execute command
    if args.command == "status":
        get_status()
    elif args.command == "start":
        start_system()
    elif args.command == "stop":
        stop_system()
    elif args.command == "restart":
        restart_system()
    elif args.command == "logs":
        view_logs(args.lines)
    elif args.command == "backup":
        backup_data()
    elif args.command == "update":
        update_system()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()