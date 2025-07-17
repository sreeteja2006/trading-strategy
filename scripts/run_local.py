#!/usr/bin/env python3
"""
Run the Trading Strategy System locally without Docker
This is useful for development or when Docker has issues
"""
import subprocess
import sys
import os
import time
import webbrowser
from pathlib import Path

def check_dependencies():
    """Check if required dependencies are installed"""
    try:
        import streamlit
        import pandas
        import plotly
        import yfinance
        print("✅ All required dependencies are installed")
        return True
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("Please install requirements: pip install -r requirements.txt")
        return False

def start_streamlit_app():
    """Start the Streamlit application"""
    # Get the project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Set environment variables
    os.environ["PYTHONPATH"] = str(project_root)
    
    print("Starting Trading Strategy System...")
    print("=" * 50)
    
    try:
        # Start Streamlit
        cmd = [
            sys.executable, "-m", "streamlit", "run", 
            "apps/main.py",
            "--server.port=8501",
            "--server.address=0.0.0.0",
            "--server.headless=true"
        ]
        
        print("Command:", " ".join(cmd))
        print("Starting Streamlit server...")
        
        # Start the process
        process = subprocess.Popen(cmd)
        
        # Wait a moment for the server to start
        time.sleep(3)
        
        print("✅ Trading Strategy System is running!")
        print("🌐 Access the website at: http://localhost:8501")
        print("📊 Available applications:")
        print("   - Trading Dashboard")
        print("   - Performance Dashboard") 
        print("   - Trading Interface")
        print("   - System Status")
        print("")
        print("Press Ctrl+C to stop the server")
        
        # Optionally open browser
        try:
            webbrowser.open("http://localhost:8501")
        except:
            pass
        
        # Wait for the process to complete
        process.wait()
        
    except KeyboardInterrupt:
        print("\n🛑 Stopping Trading Strategy System...")
        process.terminate()
        process.wait()
        print("✅ System stopped")
    except Exception as e:
        print(f"❌ Error starting system: {e}")
        return False
    
    return True

def main():
    """Main function"""
    print("Trading Strategy System - Local Runner")
    print("=" * 40)
    
    # Check if we're in the right directory
    if not os.path.exists("apps/main.py"):
        print("❌ Error: apps/main.py not found")
        print("Please run this script from the project root directory")
        sys.exit(1)
    
    # Check dependencies
    if not check_dependencies():
        sys.exit(1)
    
    # Start the application
    start_streamlit_app()

if __name__ == "__main__":
    main()