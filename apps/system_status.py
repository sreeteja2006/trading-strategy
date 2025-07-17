#!/usr/bin/env python3
"""
System Status Dashboard - Monitor the health of the trading system
"""
from flask import Blueprint, render_template, jsonify, request
import subprocess
import psutil
import os
import json
import time
from datetime import datetime, timedelta
import pandas as pd
import sqlite3

# Create a blueprint for the system status dashboard
system_bp = Blueprint('system', __name__, url_prefix='/system')

# Database setup
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'system.db')
os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

def get_db_connection():
    """Get a database connection"""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Initialize the database with tables if they don't exist"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Create system_metrics table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS system_metrics (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        timestamp TEXT NOT NULL,
        cpu_percent REAL NOT NULL,
        memory_percent REAL NOT NULL,
        disk_percent REAL NOT NULL,
        network_sent_mb REAL NOT NULL,
        network_recv_mb REAL NOT NULL
    )
    ''')
    
    # Create service_status table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS service_status (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        name TEXT NOT NULL,
        status TEXT NOT NULL,
        last_checked TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

# Initialize the database
init_db()

def get_docker_status():
    """Get status of Docker containers"""
    try:
        result = subprocess.run(
            ["docker-compose", "ps", "--format", "json"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode != 0:
            return None
            
        containers = []
        for line in result.stdout.strip().split('\n'):
            if line:
                try:
                    container = json.loads(line)
                    containers.append(container)
                except json.JSONDecodeError:
                    pass
                    
        return containers
    except Exception as e:
        return None

def get_system_metrics():
    """Get system metrics"""
    try:
        metrics = {
            "cpu_percent": psutil.cpu_percent(),
            "memory_percent": psutil.virtual_memory().percent,
            "disk_percent": psutil.disk_usage('/').percent,
            "boot_time": datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
            "uptime_hours": (datetime.now() - datetime.fromtimestamp(psutil.boot_time())).total_seconds() / 3600
        }
        
        # Get network info
        net_io = psutil.net_io_counters()
        metrics["network_sent_mb"] = net_io.bytes_sent / (1024 * 1024)
        metrics["network_recv_mb"] = net_io.bytes_recv / (1024 * 1024)
        
        # Store metrics in database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO system_metrics (timestamp, cpu_percent, memory_percent, disk_percent, network_sent_mb, network_recv_mb)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            metrics["cpu_percent"],
            metrics["memory_percent"],
            metrics["disk_percent"],
            metrics["network_sent_mb"],
            metrics["network_recv_mb"]
        ))
        
        conn.commit()
        conn.close()
        
        return metrics
    except Exception as e:
        # Return default values if there's an error
        return {
            "cpu_percent": 0,
            "memory_percent": 0,
            "disk_percent": 0,
            "boot_time": "Unknown",
            "uptime_hours": 0,
            "network_sent_mb": 0,
            "network_recv_mb": 0
        }

def get_historical_metrics(hours=1):
    """Get historical system metrics from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get metrics from the last hour
    cursor.execute('''
        SELECT * FROM system_metrics 
        WHERE timestamp >= datetime('now', ?) 
        ORDER BY timestamp ASC
    ''', (f'-{hours} hours',))
    
    rows = cursor.fetchall()
    
    timestamps = []
    cpu_values = []
    memory_values = []
    
    for row in rows:
        timestamps.append(row['timestamp'])
        cpu_values.append(row['cpu_percent'])
        memory_values.append(row['memory_percent'])
    
    conn.close()
    
    # If no data, generate sample data
    if not timestamps:
        now = datetime.now()
        timestamps = [(now - timedelta(minutes=i*5)).strftime("%Y-%m-%d %H:%M:%S") for i in range(12)]
        timestamps.reverse()
        
        # Generate sample CPU and memory values
        base_cpu = 30
        base_memory = 45
        cpu_values = [base_cpu + (i % 6) * 5 for i in range(12)]
        memory_values = [base_memory + (i % 4) * 3 for i in range(12)]
    
    return {
        'timestamps': timestamps,
        'cpu': cpu_values,
        'memory': memory_values
    }

def check_service_health(url="http://localhost:5000"):
    """Check if the web service is healthy"""
    import requests
    try:
        response = requests.get(f"{url}/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def get_service_status():
    """Get status of all services"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get service status
    cursor.execute('SELECT * FROM service_status')
    rows = cursor.fetchall()
    
    services = {}
    for row in rows:
        services[row['name']] = row['status'] == 'active'
    
    # If no services in database, add default ones
    if not services:
        services = {
            'web': True,
            'data': True,
            'trading': True
        }
        
        # Add to database
        for name, status in services.items():
            cursor.execute('''
                INSERT INTO service_status (name, status)
                VALUES (?, ?)
            ''', (name, 'active' if status else 'inactive'))
        
        conn.commit()
    
    conn.close()
    return services

@system_bp.route('/')
def system_dashboard():
    """Render the system status dashboard"""
    metrics = get_system_metrics()
    resource_data = get_historical_metrics()
    containers = get_docker_status() or []
    services = get_service_status()
    
    return render_template(
        'system.html',
        metrics=metrics,
        resource_data=json.dumps(resource_data),
        containers=containers,
        services=services,
        last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

@system_bp.route('/api/metrics')
def api_metrics():
    """API endpoint for system metrics"""
    metrics = get_system_metrics()
    return jsonify(metrics)

@system_bp.route('/api/historical_metrics')
def api_historical_metrics():
    """API endpoint for historical system metrics"""
    hours = request.args.get('hours', 1, type=int)
    data = get_historical_metrics(hours)
    return jsonify(data)

@system_bp.route('/api/containers')
def api_containers():
    """API endpoint for container status"""
    containers = get_docker_status()
    return jsonify(containers or [])

@system_bp.route('/api/services')
def api_services():
    """API endpoint for service status"""
    services = get_service_status()
    return jsonify(services)

@system_bp.route('/api/update_service', methods=['POST'])
def update_service():
    """API endpoint to update service status"""
    try:
        data = request.get_json()
        name = data.get('name')
        status = data.get('status')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE service_status 
            SET status = ?, last_checked = CURRENT_TIMESTAMP
            WHERE name = ?
        ''', (status, name))
        
        if cursor.rowcount == 0:
            cursor.execute('''
                INSERT INTO service_status (name, status)
                VALUES (?, ?)
            ''', (name, status))
        
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success', 'message': f'Service {name} updated to {status}'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@system_bp.route('/api/restart', methods=['POST'])
def restart_services():
    """API endpoint to restart services"""
    try:
        service = request.args.get('service', 'all')
        
        if service == 'all':
            result = subprocess.run(["docker-compose", "restart"], check=True, capture_output=True)
        else:
            result = subprocess.run(["docker-compose", "restart", service], check=True, capture_output=True)
        
        return jsonify({'status': 'success', 'message': f'Services restarted successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@system_bp.route('/api/logs')
def get_logs():
    """API endpoint to get logs"""
    try:
        service = request.args.get('service', 'all')
        lines = request.args.get('lines', 10, type=int)
        
        if service == 'all':
            result = subprocess.run(
                ["docker-compose", "logs", f"--tail={lines}"],
                capture_output=True,
                text=True,
                check=False
            )
        else:
            result = subprocess.run(
                ["docker-compose", "logs", f"--tail={lines}", service],
                capture_output=True,
                text=True,
                check=False
            )
        
        if result.returncode == 0:
            return jsonify({'status': 'success', 'logs': result.stdout})
        else:
            return jsonify({'status': 'error', 'message': 'Could not retrieve logs'}), 500
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@system_bp.route('/api/backup', methods=['POST'])
def create_backup():
    """API endpoint to create a backup"""
    try:
        backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'backups')
        os.makedirs(backup_dir, exist_ok=True)
        
        backup_file = os.path.join(backup_dir, f"backup_{backup_time}.tar.gz")
        backup_cmd = f"tar -czf {backup_file} data config"
        
        subprocess.run(backup_cmd, shell=True, check=True)
        
        return jsonify({
            'status': 'success', 
            'message': f'Backup created: {os.path.basename(backup_file)}',
            'file': os.path.basename(backup_file)
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500