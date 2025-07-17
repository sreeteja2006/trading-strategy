import os
import argparse
import subprocess
import sys

def run_command(command, description):
    """Run a shell command and handle errors"""
    print(f"Running: {description}")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✓ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"✗ {description} failed: {e}")
        if e.stderr:
            print(f"Error: {e.stderr}")
        return False

def deploy_local():
    """Deploy the application locally using Docker Compose"""
    print("🚀 Starting local deployment...")
    
    # Stop any existing containers
    run_command("docker-compose down", "Stopping existing containers")
    
    # Build and start the application
    if not run_command("docker-compose build", "Building Docker image"):
        return False
    
    if not run_command("docker-compose up -d", "Starting application"):
        return False
    
    print("\n✅ Deployment successful!")
    print("📊 Your trading strategy is now running at: http://localhost:8080")
    print("📋 To view logs: docker-compose logs -f")
    print("🛑 To stop: docker-compose down")
    
    return True

def deploy_production():
    """Deploy for production (without AWS)"""
    print("🚀 Starting production deployment...")
    
    # Build optimized image
    if not run_command("docker build -t trading-strategy:latest .", "Building production image"):
        return False
    
    # Stop existing container if running
    run_command("docker stop trading-strategy-prod 2>/dev/null || true", "Stopping existing container")
    run_command("docker rm trading-strategy-prod 2>/dev/null || true", "Removing existing container")
    
    # Run in production mode
    prod_command = """docker run -d \
        --name trading-strategy-prod \
        --restart unless-stopped \
        -p 8080:8080 \
        -v $(pwd)/data:/app/data \
        -v $(pwd)/reports:/app/reports \
        -e PYTHONPATH=/app \
        -e MATPLOTLIB_BACKEND=Agg \
        trading-strategy:latest"""
    
    if not run_command(prod_command, "Starting production container"):
        return False
    
    print("\n✅ Production deployment successful!")
    print("📊 Application running on port 8080")
    print("📋 To view logs: docker logs -f trading-strategy-prod")
    print("🛑 To stop: docker stop trading-strategy-prod")
    
    return True

def show_status():
    """Show current deployment status"""
    print("📊 Current deployment status:")
    run_command("docker ps | grep trading", "Checking running containers")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Deploy trading strategy application")
    parser.add_argument("--mode", choices=["local", "production", "status"], 
                       default="local", help="Deployment mode")
    args = parser.parse_args()
    
    if args.mode == "local":
        deploy_local()
    elif args.mode == "production":
        deploy_production()
    elif args.mode == "status":
        show_status()