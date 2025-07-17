#!/usr/bin/env python3
"""
Main Flask Application for Trading Strategy System
"""
from flask import Flask, render_template, jsonify, redirect, url_for, request
import os
from datetime import datetime
import psutil
import sqlite3
import json

# Create necessary directories
os.makedirs('data', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)
os.makedirs('data/raw', exist_ok=True)
os.makedirs('data/results', exist_ok=True)
os.makedirs('logs', exist_ok=True)

# Import blueprints
from apps.performance_dashboard import performance_bp
from apps.system_status import system_bp

app = Flask(__name__)

# Register blueprints
app.register_blueprint(performance_bp)
app.register_blueprint(system_bp)

@app.route('/')
def index():
    """Home page"""
    # System overview data
    system_data = {
        'active_strategies': 3,
        'todays_trades': 12,
        'portfolio_value': '₹1,250,000',
        'portfolio_change': '+2.3%',
        'system_uptime': '99.8%'
    }
    
    # Recent activity
    activity_data = [
        {"time": "10:15 AM", "event": "Buy signal generated for RELIANCE"},
        {"time": "10:30 AM", "event": "Executed buy order: 5 RELIANCE @ ₹2,450.75"},
        {"time": "11:45 AM", "event": "Portfolio rebalanced"},
        {"time": "01:30 PM", "event": "Sell signal generated for TCS"},
        {"time": "01:35 PM", "event": "Executed sell order: 10 TCS @ ₹3,560.25"}
    ]
    
    # Available apps
    apps = [
        {
            "id": "dashboard",
            "title": "📈 Trading Dashboard",
            "description": "Monitor real-time market data and technical indicators",
            "url": "/dashboard"
        },
        {
            "id": "performance",
            "title": "💰 Performance Dashboard",
            "description": "Track your trading strategy results and portfolio performance",
            "url": "/performance"
        },
        {
            "id": "trading",
            "title": "🚀 Trading Interface",
            "description": "Execute trades and manage your trading strategy",
            "url": "/trading"
        },
        {
            "id": "system",
            "title": "🖥️ System Status",
            "description": "Monitor system health, resources, and container status",
            "url": "/system"
        }
    ]
    
    return render_template(
        'index.html',
        system_data=system_data,
        activity=activity_data,
        apps=apps,
        current_time=datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    )

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({"status": "healthy"})

@app.route('/api/system_info')
def system_info():
    """API endpoint for system information"""
    try:
        # Check if we're running in Docker
        in_docker = os.path.exists("/.dockerenv")
        
        # Get memory usage
        memory_usage = psutil.virtual_memory().percent
        
        return jsonify({
            "status": "success",
            "data": {
                "environment": "Docker" if in_docker else "Local",
                "memory_usage": f"{memory_usage:.1f}%",
                "server_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
        })
    except Exception as e:
        return jsonify({"status": "error", "message": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)