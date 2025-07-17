#!/usr/bin/env python3
"""
Main Web Application - Entry point for all trading strategy apps
"""
import streamlit as st
import sys
import os
import importlib
import subprocess
from datetime import datetime

# Set page configuration
st.set_page_config(
    page_title="Trading Strategy System",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Define available apps
APPS = {
    "dashboard": {
        "title": "📈 Trading Dashboard",
        "description": "Monitor real-time market data and technical indicators",
        "module": "apps.dashboard",
        "function": "main"
    },
    "performance": {
        "title": "💰 Performance Dashboard",
        "description": "Track your trading strategy results and portfolio performance",
        "module": "apps.performance_dashboard",
        "function": "main"
    },
    "trading": {
        "title": "🚀 Trading Interface",
        "description": "Execute trades and manage your trading strategy",
        "module": "apps.trading_interface",
        "function": "main"
    },
    "system": {
        "title": "🖥️ System Status",
        "description": "Monitor system health, resources, and container status",
        "module": "apps.system_status",
        "function": "main"
    }
}

def main():
    """Main function to run the web application"""
    
    # Sidebar navigation
    st.sidebar.title("Trading Strategy System")
    st.sidebar.image("https://img.icons8.com/color/96/000000/stocks.png", width=100)
    
    # System status
    system_status = "🟢 Online"
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    st.sidebar.markdown(f"**Status:** {system_status}")
    st.sidebar.markdown(f"**Server Time:** {current_time}")
    
    # App selection
    st.sidebar.markdown("## Navigation")
    
    # Default to home page
    app_selection = st.sidebar.radio(
        "Select Application",
        ["Home"] + list(APPS.keys()),
        format_func=lambda x: "🏠 Home" if x == "Home" else APPS[x]["title"] if x in APPS else x
    )
    
    # Divider
    st.sidebar.markdown("---")
    
    # System information
    st.sidebar.markdown("## System Information")
    
    # Check if we're running in Docker
    in_docker = os.path.exists("/.dockerenv")
    st.sidebar.markdown(f"**Environment:** {'🐳 Docker' if in_docker else '💻 Local'}")
    
    # Display memory usage
    try:
        import psutil
        memory_usage = f"{psutil.virtual_memory().percent:.1f}%"
        st.sidebar.markdown(f"**Memory Usage:** {memory_usage}")
    except:
        st.sidebar.markdown("**Memory Usage:** Not available")
    
    # Footer
    st.sidebar.markdown("---")
    st.sidebar.markdown("© 2025 Trading Strategy System")
    
    # Main content area
    if app_selection == "Home":
        show_home_page()
    else:
        # Run the selected app
        try:
            app_info = APPS[app_selection]
            
            # Clear any existing content
            st.empty()
            
            # Import and run the selected app
            if app_selection == "dashboard":
                from apps.dashboard import main as dashboard_main
                dashboard_main()
            elif app_selection == "performance":
                from apps.performance_dashboard import main as performance_main
                performance_main()
            elif app_selection == "trading":
                from apps.trading_interface import main as trading_main
                trading_main()
            elif app_selection == "system":
                from apps.system_status import main as system_main
                system_main()
            else:
                st.error(f"Unknown application: {app_selection}")
                
        except Exception as e:
            st.error(f"Error loading application: {str(e)}")
            st.code(f"Exception: {e}")
            import traceback
            st.code(traceback.format_exc())

def show_home_page():
    """Display the home page with app cards"""
    st.title("🏠 Trading Strategy System")
    st.markdown("Welcome to your all-in-one trading strategy platform")
    
    st.markdown("### Available Applications")
    
    # Create columns for app cards
    cols = st.columns(len(APPS))
    
    # Display app cards
    for i, (app_id, app_info) in enumerate(APPS.items()):
        with cols[i]:
            st.markdown(f"### {app_info['title']}")
            st.markdown(app_info['description'])
            
            if st.button(f"Launch {app_info['title']}", key=f"btn_{app_id}"):
                # Set query parameter to navigate to the app
                st.query_params["app"] = app_id
                st.rerun()
    
    # System overview
    st.markdown("---")
    st.markdown("## System Overview")
    
    # Create metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Active Strategies", "3")
    
    with col2:
        st.metric("Today's Trades", "12")
    
    with col3:
        st.metric("Portfolio Value", "₹1,250,000", "+2.3%")
    
    with col4:
        st.metric("System Uptime", "99.8%")
    
    # Recent activity
    st.markdown("### Recent Activity")
    
    # Sample activity data
    activity_data = [
        {"time": "10:15 AM", "event": "Buy signal generated for RELIANCE"},
        {"time": "10:30 AM", "event": "Executed buy order: 5 RELIANCE @ ₹2,450.75"},
        {"time": "11:45 AM", "event": "Portfolio rebalanced"},
        {"time": "01:30 PM", "event": "Sell signal generated for TCS"},
        {"time": "01:35 PM", "event": "Executed sell order: 10 TCS @ ₹3,560.25"}
    ]
    
    for activity in activity_data:
        st.markdown(f"**{activity['time']}** - {activity['event']}")
    
    # Documentation link
    st.markdown("---")
    st.markdown("📚 [View Documentation](/docs)")

if __name__ == "__main__":
    main()