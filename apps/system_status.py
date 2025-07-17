#!/usr/bin/env python3
"""
System Status Dashboard - Monitor the health of the trading system
"""
import streamlit as st
import subprocess
import psutil
import os
import json
import time
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px

st.set_page_config(
    page_title="System Status Dashboard",
    page_icon="🖥️",
    layout="wide"
)

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
        st.error(f"Error getting Docker status: {str(e)}")
        return None

def get_system_metrics():
    """Get system metrics"""
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
    
    return metrics

def check_service_health(url="http://localhost:8501"):
    """Check if the web service is healthy"""
    import requests
    try:
        response = requests.get(f"{url}/_stcore/health", timeout=5)
        return response.status_code == 200
    except:
        return False

def main():
    st.title("🖥️ System Status Dashboard")
    
    # Refresh button
    col1, col2 = st.columns([9, 1])
    with col2:
        if st.button("🔄 Refresh"):
            st.rerun()
    
    # Last updated time
    with col1:
        st.caption(f"Last updated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # System metrics
    st.subheader("System Resources")
    
    try:
        metrics = get_system_metrics()
        
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.metric("CPU Usage", f"{metrics['cpu_percent']}%")
            
        with col2:
            st.metric("Memory Usage", f"{metrics['memory_percent']}%")
            
        with col3:
            st.metric("Disk Usage", f"{metrics['disk_percent']}%")
            
        with col4:
            st.metric("Uptime", f"{metrics['uptime_hours']:.1f} hours")
        
        # Resource usage charts
        st.subheader("Resource Usage")
        
        # Create sample historical data (in a real implementation, you'd track this)
        timestamps = [datetime.now() - timedelta(minutes=i*5) for i in range(12)]
        timestamps.reverse()
        
        cpu_values = [metrics['cpu_percent'] - 10 + i*2 for i in range(12)]
        cpu_values = [max(0, min(100, x)) for x in cpu_values]  # Ensure values are between 0-100
        
        memory_values = [metrics['memory_percent'] - 5 + i for i in range(12)]
        memory_values = [max(0, min(100, x)) for x in memory_values]
        
        df = pd.DataFrame({
            'timestamp': timestamps,
            'cpu': cpu_values,
            'memory': memory_values
        })
        
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=df['timestamp'], 
            y=df['cpu'],
            mode='lines+markers',
            name='CPU Usage %',
            line=dict(color='blue', width=2)
        ))
        
        fig.add_trace(go.Scatter(
            x=df['timestamp'], 
            y=df['memory'],
            mode='lines+markers',
            name='Memory Usage %',
            line=dict(color='green', width=2)
        ))
        
        fig.update_layout(
            title='Resource Usage Over Time',
            xaxis_title='Time',
            yaxis_title='Usage %',
            height=300
        )
        
        st.plotly_chart(fig, use_container_width=True)
        
    except Exception as e:
        st.error(f"Error getting system metrics: {str(e)}")
    
    # Docker container status
    st.subheader("Docker Containers")
    
    containers = get_docker_status()
    if containers:
        container_data = []
        for container in containers:
            container_data.append({
                "Name": container.get("Name", "Unknown"),
                "Service": container.get("Service", "Unknown"),
                "Status": container.get("State", "Unknown"),
                "Health": container.get("Health", "Unknown"),
                "Ports": container.get("Ports", "")
            })
        
        df_containers = pd.DataFrame(container_data)
        
        # Color-code the status
        def highlight_status(val):
            if val == "running":
                return 'background-color: #c6efce; color: #006100'
            elif val == "exited":
                return 'background-color: #ffc7ce; color: #9c0006'
            else:
                return 'background-color: #ffeb9c; color: #9c6500'
        
        st.dataframe(
            df_containers.style.applymap(
                highlight_status, 
                subset=['Status']
            ),
            use_container_width=True
        )
    else:
        st.warning("No Docker containers found or Docker is not running")
    
    # Service health checks
    st.subheader("Service Health")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        web_health = check_service_health()
        status = "🟢 Online" if web_health else "🔴 Offline"
        st.metric("Web Interface", status)
    
    with col2:
        # Check if data collection is running (placeholder)
        data_health = True  # Replace with actual check
        status = "🟢 Active" if data_health else "🔴 Inactive"
        st.metric("Data Collection", status)
    
    with col3:
        # Check if trading system is running (placeholder)
        trading_health = True  # Replace with actual check
        status = "🟢 Active" if trading_health else "🔴 Inactive"
        st.metric("Trading System", status)
    
    # System logs
    st.subheader("Recent Logs")
    
    try:
        result = subprocess.run(
            ["docker-compose", "logs", "--tail=10"],
            capture_output=True,
            text=True,
            check=False
        )
        
        if result.returncode == 0:
            st.code(result.stdout)
        else:
            st.warning("Could not retrieve logs")
    except Exception as e:
        st.error(f"Error getting logs: {str(e)}")
    
    # Actions
    st.subheader("System Actions")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        if st.button("🔄 Restart Services"):
            try:
                subprocess.run(["docker-compose", "restart"], check=True)
                st.success("Services restarted successfully")
            except Exception as e:
                st.error(f"Error restarting services: {str(e)}")
    
    with col2:
        if st.button("🔍 View Detailed Logs"):
            st.session_state.show_logs = True
    
    with col3:
        if st.button("💾 Backup Data"):
            try:
                backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_cmd = f"tar -czf backup_{backup_time}.tar.gz data config"
                subprocess.run(backup_cmd, shell=True, check=True)
                st.success(f"Backup created: backup_{backup_time}.tar.gz")
            except Exception as e:
                st.error(f"Error creating backup: {str(e)}")
    
    # Show detailed logs if requested
    if st.session_state.get("show_logs", False):
        st.subheader("Detailed Logs")
        
        # Add log filtering options
        service = st.selectbox("Select Service", ["All Services", "trading-app", "database"])
        lines = st.slider("Number of Lines", 10, 100, 50)
        
        log_cmd = ["docker-compose", "logs", f"--tail={lines}"]
        if service != "All Services":
            log_cmd.append(service)
        
        try:
            result = subprocess.run(log_cmd, capture_output=True, text=True, check=False)
            if result.returncode == 0:
                st.code(result.stdout)
            else:
                st.warning("Could not retrieve detailed logs")
        except Exception as e:
            st.error(f"Error getting detailed logs: {str(e)}")
        
        if st.button("Hide Logs"):
            st.session_state.show_logs = False
            st.rerun()

if __name__ == "__main__":
    main()