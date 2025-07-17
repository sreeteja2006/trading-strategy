#!/usr/bin/env python3
"""
Real Broker Integration - Connect to Indian brokers
"""
import sys
sys.path.append('scripts')

import requests
import json
import hashlib
import hmac
from datetime import datetime, timedelta
import pandas as pd
import os
from typing import Dict, List, Optional

class ZerodhaKiteAPI:
    """Zerodha Kite API Integration"""
    
    def __init__(self, api_key: str, api_secret: str, access_token: str = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.base_url = "https://api.kite.trade"
        self.session = requests.Session()
        
        if access_token:
            self.session.headers.update({
                'Authorization': f'token {api_key}:{access_token}',
                'X-Kite-Version': '3'
            })
    
    def generate_session(self, request_token: str) -> Dict:
        """Generate access token from request token"""
        url = f"{self.base_url}/session/token"
        
        checksum = hashlib.sha256(
            f"{self.api_key}{request_token}{self.api_secret}".encode()
        ).hexdigest()
        
        data = {
            'api_key': self.api_key,
            'request_token': request_token,
            'checksum': checksum
        }
        
        response = requests.post(url, data=data)
        return response.json()
    
    def get_profile(self) -> Dict:
        """Get user profile"""
        url = f"{self.base_url}/user/profile"
        response = self.session.get(url)
        return response.json()
    
    def get_positions(self) -> List[Dict]:
        """Get current positions"""
        url = f"{self.base_url}/portfolio/positions"
        response = self.session.get(url)
        return response.json().get('data', [])
    
    def get_holdings(self) -> List[Dict]:
        """Get current holdings"""
        url = f"{self.base_url}/portfolio/holdings"
        response = self.session.get(url)
        return response.json().get('data', [])
    
    def get_funds(self) -> Dict:
        """Get account funds"""
        url = f"{self.base_url}/user/margins"
        response = self.session.get(url)
        return response.json().get('data', {})
    
    def place_order(self, symbol: str, quantity: int, order_type: str = 'MARKET', 
                   transaction_type: str = 'BUY', product: str = 'CNC') -> Dict:
        """Place an order"""
        url = f"{self.base_url}/orders/regular"
        
        data = {
            'tradingsymbol': symbol,
            'exchange': 'NSE',
            'transaction_type': transaction_type,
            'order_type': order_type,
            'quantity': quantity,
            'product': product,
            'validity': 'DAY'
        }
        
        response = self.session.post(url, data=data)
        return response.json()
    
    def get_orders(self) -> List[Dict]:
        """Get order history"""
        url = f"{self.base_url}/orders"
        response = self.session.get(url)
        return response.json().get('data', [])
    
    def get_ltp(self, instruments: List[str]) -> Dict:
        """Get Last Traded Price for instruments"""
        url = f"{self.base_url}/quote/ltp"
        params = {'i': instruments}
        response = self.session.get(url, params=params)
        return response.json().get('data', {})

class UpstoxAPI:
    """Upstox API Integration"""
    
    def __init__(self, api_key: str, api_secret: str, access_token: str = None):
        self.api_key = api_key
        self.api_secret = api_secret
        self.access_token = access_token
        self.base_url = "https://api.upstox.com/v2"
        self.session = requests.Session()
        
        if access_token:
            self.session.headers.update({
                'Authorization': f'Bearer {access_token}',
                'Accept': 'application/json'
            })
    
    def get_profile(self) -> Dict:
        """Get user profile"""
        url = f"{self.base_url}/user/profile"
        response = self.session.get(url)
        return response.json()
    
    def get_positions(self) -> Dict:
        """Get current positions"""
        url = f"{self.base_url}/portfolio/short-term-positions"
        response = self.session.get(url)
        return response.json()
    
    def place_order(self, symbol: str, quantity: int, order_type: str = 'MARKET',
                   transaction_type: str = 'BUY', product: str = 'D') -> Dict:
        """Place an order"""
        url = f"{self.base_url}/order/place"
        
        data = {
            'instrument_token': symbol,
            'quantity': quantity,
            'product': product,
            'validity': 'DAY',
            'price': 0,
            'tag': 'trading-bot',
            'instrument_token': f'NSE_EQ|INE002A01018',  # Example for Reliance
            'order_type': order_type,
            'transaction_type': transaction_type
        }
        
        response = self.session.post(url, json=data)
        return response.json()

class BrokerManager:
    """Unified broker management"""
    
    def __init__(self, broker_type: str = 'zerodha'):
        self.broker_type = broker_type
        self.broker_api = None
        self.is_connected = False
        
        # Load credentials from environment or config
        self.load_credentials()
    
    def load_credentials(self):
        """Load broker credentials from environment variables"""
        if self.broker_type == 'zerodha':
            api_key = os.getenv('ZERODHA_API_KEY')
            api_secret = os.getenv('ZERODHA_API_SECRET')
            access_token = os.getenv('ZERODHA_ACCESS_TOKEN')
            
            if api_key and api_secret:
                self.broker_api = ZerodhaKiteAPI(api_key, api_secret, access_token)
                self.is_connected = access_token is not None
        
        elif self.broker_type == 'upstox':
            api_key = os.getenv('UPSTOX_API_KEY')
            api_secret = os.getenv('UPSTOX_API_SECRET')
            access_token = os.getenv('UPSTOX_ACCESS_TOKEN')
            
            if api_key and api_secret:
                self.broker_api = UpstoxAPI(api_key, api_secret, access_token)
                self.is_connected = access_token is not None
    
    def connect(self, request_token: str = None) -> bool:
        """Connect to broker API"""
        if not self.broker_api:
            print("❌ Broker API not initialized. Check credentials.")
            return False
        
        try:
            if self.broker_type == 'zerodha' and request_token:
                # Generate session for Zerodha
                session_data = self.broker_api.generate_session(request_token)
                if 'data' in session_data:
                    self.broker_api.access_token = session_data['data']['access_token']
                    self.broker_api.session.headers.update({
                        'Authorization': f'token {self.broker_api.api_key}:{self.broker_api.access_token}'
                    })
                    self.is_connected = True
                    print("✅ Connected to Zerodha Kite API")
                    return True
            
            # Test connection
            profile = self.broker_api.get_profile()
            if 'data' in profile or 'status' in profile:
                self.is_connected = True
                print(f"✅ Connected to {self.broker_type.title()} API")
                return True
                
        except Exception as e:
            print(f"❌ Connection failed: {e}")
            
        return False
    
    def get_account_info(self) -> Dict:
        """Get account information"""
        if not self.is_connected:
            return {'error': 'Not connected to broker'}
        
        try:
            profile = self.broker_api.get_profile()
            funds = self.broker_api.get_funds() if hasattr(self.broker_api, 'get_funds') else {}
            positions = self.broker_api.get_positions()
            
            return {
                'profile': profile,
                'funds': funds,
                'positions': positions,
                'broker': self.broker_type
            }
        except Exception as e:
            return {'error': str(e)}
    
    def place_trade(self, symbol: str, quantity: int, action: str) -> Dict:
        """Place a trade order"""
        if not self.is_connected:
            return {'status': 'error', 'message': 'Not connected to broker'}
        
        try:
            transaction_type = 'BUY' if action.upper() == 'BUY' else 'SELL'
            
            result = self.broker_api.place_order(
                symbol=symbol,
                quantity=quantity,
                transaction_type=transaction_type,
                order_type='MARKET'
            )
            
            return {
                'status': 'success' if 'order_id' in str(result) else 'error',
                'result': result,
                'symbol': symbol,
                'quantity': quantity,
                'action': action
            }
            
        except Exception as e:
            return {
                'status': 'error',
                'message': str(e),
                'symbol': symbol,
                'quantity': quantity,
                'action': action
            }
    
    def get_current_price(self, symbol: str) -> float:
        """Get current market price"""
        if not self.is_connected:
            return None
        
        try:
            if self.broker_type == 'zerodha':
                ltp_data = self.broker_api.get_ltp([f'NSE:{symbol}'])
                return ltp_data.get(f'NSE:{symbol}', {}).get('last_price')
            
            # Add other broker implementations
            return None
            
        except Exception as e:
            print(f"Error getting price for {symbol}: {e}")
            return None

def setup_broker_credentials():
    """Interactive setup for broker credentials"""
    print("🔧 Broker API Setup")
    print("=" * 30)
    
    broker = input("Select broker (zerodha/upstox): ").lower()
    
    if broker == 'zerodha':
        print("\n📋 Zerodha Kite API Setup:")
        print("1. Go to https://kite.trade/")
        print("2. Login and go to Console > API")
        print("3. Create a new app to get API Key and Secret")
        print("4. For access token, you'll need to complete OAuth flow")
        
        api_key = input("\nEnter API Key: ")
        api_secret = input("Enter API Secret: ")
        
        # Save to environment file
        with open('.env', 'w') as f:
            f.write(f"ZERODHA_API_KEY={api_key}\n")
            f.write(f"ZERODHA_API_SECRET={api_secret}\n")
            f.write("# Add ZERODHA_ACCESS_TOKEN after OAuth\n")
        
        print("✅ Credentials saved to .env file")
        print("⚠️  You'll need to complete OAuth to get access token")
        
    elif broker == 'upstox':
        print("\n📋 Upstox API Setup:")
        print("1. Go to https://upstox.com/developer/")
        print("2. Create developer account and app")
        
        api_key = input("\nEnter API Key: ")
        api_secret = input("Enter API Secret: ")
        
        with open('.env', 'w') as f:
            f.write(f"UPSTOX_API_KEY={api_key}\n")
            f.write(f"UPSTOX_API_SECRET={api_secret}\n")
            f.write("# Add UPSTOX_ACCESS_TOKEN after OAuth\n")
        
        print("✅ Credentials saved to .env file")

def test_broker_connection():
    """Test broker API connection"""
    print("🧪 Testing Broker Connection")
    print("=" * 30)
    
    # Try to connect to broker
    broker = BrokerManager('zerodha')  # Default to Zerodha
    
    if not broker.broker_api:
        print("❌ No broker credentials found")
        print("Run setup_broker_credentials() first")
        return False
    
    # Test connection (will fail without proper access token)
    if broker.connect():
        account_info = broker.get_account_info()
        print("✅ Connection successful!")
        print(f"Account: {account_info}")
        return True
    else:
        print("❌ Connection failed")
        print("Make sure you have valid access token")
        return False

if __name__ == "__main__":
    print("🏦 Broker Integration Module")
    print("=" * 40)
    
    choice = input("1. Setup credentials\n2. Test connection\nChoice (1/2): ")
    
    if choice == '1':
        setup_broker_credentials()
    elif choice == '2':
        test_broker_connection()
    else:
        print("Invalid choice")