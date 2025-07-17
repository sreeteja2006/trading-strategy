#!/usr/bin/env python3
"""
Health check script for the Trading Strategy System website
"""
import requests
import sys
import os

def check_health():
    """Check if the Streamlit app is healthy"""
    try:
        # Check if the Streamlit health endpoint is accessible
        response = requests.get("http://localhost:8501/_stcore/health", timeout=5)
        
        if response.status_code == 200:
            print("✅ Website is healthy")
            return True
        else:
            print(f"❌ Website returned status code: {response.status_code}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to website")
        return False
    except requests.exceptions.Timeout:
        print("❌ Website health check timed out")
        return False
    except Exception as e:
        print(f"❌ Health check failed: {str(e)}")
        return False

if __name__ == "__main__":
    if check_health():
        sys.exit(0)
    else:
        sys.exit(1)