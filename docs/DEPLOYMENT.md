# Deployment Guide

## Prerequisites

### Installing Docker on Arch Linux
```bash
# Install Docker and Docker Compose
sudo pacman -S docker docker-compose

# Start and enable Docker service
sudo systemctl start docker
sudo systemctl enable docker

# Add your user to docker group
sudo usermod -aG docker $USER

# Log out and log back in, or run:
newgrp docker
```

## Local Deployment

1. Build and run with Docker:
```bash
docker build -t trading-strategy .
docker run -d --env-file .env trading-strategy
```

2. Run with Docker Compose:
```bash
docker compose up -d
```

## AWS Deployment

1. Configure AWS CLI:
```bash
aws configure
```

2. Run deployment script:
```bash
python scripts/deploy.py --region us-east-1
```

## Environment Variables

Copy `.env.example` to `.env` and fill in your values:
```bash
cp .env.example .env
nano .env
```