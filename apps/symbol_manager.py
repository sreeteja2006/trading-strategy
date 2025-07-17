#!/usr/bin/env python3
"""
Symbol Manager - Search and manage trading symbols
"""
from flask import Blueprint, render_template, jsonify, request
import yfinance as yf
import json
import os
import sqlite3
from datetime import datetime

symbol_bp = Blueprint('symbols', __name__, url_prefix='/symbols')

# Database setup
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'watchlist.db')
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
    
    # Create watchlist table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS watchlist (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL UNIQUE,
        name TEXT NOT NULL,
        market TEXT NOT NULL,
        added_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

# Initialize the database
init_db()

@symbol_bp.route('/')
def manage_symbols():
    """Render the symbol management page"""
    return render_template('manage_symbols.html')

@symbol_bp.route('/api/search_symbols')
def search_symbols():
    """API endpoint to search for symbols"""
    query = request.args.get('query', '')
    market = request.args.get('market', 'all')
    
    if not query:
        return jsonify({'status': 'error', 'message': 'Query is required'}), 400
    
    try:
        # Use yfinance to search for symbols
        results = []
        
        # For demonstration, we'll use a simple approach
        # In a production app, you might want to use a more robust API
        
        # Try exact symbol match first
        try:
            ticker = yf.Ticker(query)
            info = ticker.info
            
            if info and 'symbol' in info:
                market_type = get_market_type(info)
                
                if market == 'all' or market == market_type.lower():
                    results.append({
                        'symbol': info['symbol'],
                        'name': info.get('longName', info.get('shortName', 'Unknown')),
                        'market': market_type,
                        'price': info.get('regularMarketPrice', None),
                        'change': info.get('regularMarketChangePercent', None)
                    })
        except:
            pass
        
        # If no exact match or we want more results, try search
        if not results:
            # This is a simplified approach - in a real app, you'd use a proper stock API
            # that supports searching by name/keyword
            common_symbols = {
                # Indian Stocks
                'RELIANCE': 'Reliance Industries Ltd',
                'TCS': 'Tata Consultancy Services Ltd',
                'INFY': 'Infosys Ltd',
                'HDFCBANK': 'HDFC Bank Ltd',
                'ICICIBANK': 'ICICI Bank Ltd',
                'SBIN': 'State Bank of India',
                'HINDUNILVR': 'Hindustan Unilever Ltd',
                'BHARTIARTL': 'Bharti Airtel Ltd',
                'ITC': 'ITC Ltd',
                'KOTAKBANK': 'Kotak Mahindra Bank Ltd',
                
                # Nifty Indices
                'NIFTY50': 'Nifty 50 Index',
                'NIFTYBANK': 'Nifty Bank Index',
                'NIFTYMIDCAP': 'Nifty Midcap 100 Index',
                'NIFTYSMALL': 'Nifty Smallcap 100 Index',
                'NIFTYIT': 'Nifty IT Index',
                'NIFTYPHARMA': 'Nifty Pharma Index',
                
                # Commodities
                'GOLD': 'Gold Futures',
                'SILVER': 'Silver Futures',
                'CRUDEOIL': 'Crude Oil Futures',
                'NATURALGAS': 'Natural Gas Futures',
                'COPPER': 'Copper Futures',
                
                # US Stocks
                'AAPL': 'Apple Inc',
                'MSFT': 'Microsoft Corporation',
                'GOOGL': 'Alphabet Inc',
                'AMZN': 'Amazon.com Inc',
                'META': 'Meta Platforms Inc',
                'TSLA': 'Tesla Inc',
                'NVDA': 'NVIDIA Corporation',
                'JPM': 'JPMorgan Chase & Co',
                'V': 'Visa Inc',
                'JNJ': 'Johnson & Johnson'
            }
            
            query_upper = query.upper()
            
            # Filter symbols based on query
            for symbol, name in common_symbols.items():
                if (query_upper in symbol) or (query.lower() in name.lower()):
                    market_type = 'Stocks'
                    if 'NIFTY' in symbol:
                        market_type = 'Indices'
                    elif symbol in ['GOLD', 'SILVER', 'CRUDEOIL', 'NATURALGAS', 'COPPER']:
                        market_type = 'Commodities'
                    
                    if market == 'all' or market == market_type.lower():
                        # Try to get current price
                        price = None
                        change = None
                        try:
                            ticker = yf.Ticker(symbol)
                            hist = ticker.history(period='1d')
                            if not hist.empty:
                                price = hist['Close'].iloc[-1]
                                if len(hist) > 1:
                                    prev_close = hist['Close'].iloc[-2]
                                    change = ((price - prev_close) / prev_close) * 100
                        except:
                            pass
                        
                        results.append({
                            'symbol': symbol,
                            'name': name,
                            'market': market_type,
                            'price': price,
                            'change': change
                        })
        
        return jsonify({'status': 'success', 'data': results})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def get_market_type(ticker_info):
    """Determine the market type based on ticker info"""
    if 'quoteType' in ticker_info:
        quote_type = ticker_info['quoteType']
        if quote_type == 'EQUITY':
            return 'Stocks'
        elif quote_type == 'ETF':
            return 'ETFs'
        elif quote_type == 'INDEX':
            return 'Indices'
        elif quote_type in ['CURRENCY', 'CRYPTOCURRENCY']:
            return 'Forex'
    
    # Default to stocks
    return 'Stocks'

@symbol_bp.route('/api/watchlist')
def get_watchlist():
    """API endpoint to get the user's watchlist"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM watchlist ORDER BY added_date DESC')
        rows = cursor.fetchall()
        
        watchlist = []
        for row in rows:
            symbol = row['symbol']
            
            # Try to get current price and change
            price = None
            change = None
            try:
                ticker = yf.Ticker(symbol)
                hist = ticker.history(period='2d')
                if not hist.empty:
                    price = hist['Close'].iloc[-1]
                    if len(hist) > 1:
                        prev_close = hist['Close'].iloc[-2]
                        change = ((price - prev_close) / prev_close) * 100
            except:
                pass
            
            watchlist.append({
                'symbol': symbol,
                'name': row['name'],
                'market': row['market'],
                'price': price,
                'change': change
            })
        
        conn.close()
        return jsonify({'status': 'success', 'data': watchlist})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@symbol_bp.route('/api/watchlist/add', methods=['POST'])
def add_to_watchlist():
    """API endpoint to add a symbol to the watchlist"""
    try:
        data = request.get_json()
        
        if not data or 'symbol' not in data or 'name' not in data or 'market' not in data:
            return jsonify({'status': 'error', 'message': 'Missing required fields'}), 400
        
        symbol = data['symbol']
        name = data['name']
        market = data['market']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if symbol already exists
        cursor.execute('SELECT * FROM watchlist WHERE symbol = ?', (symbol,))
        existing = cursor.fetchone()
        
        if existing:
            conn.close()
            return jsonify({'status': 'error', 'message': 'Symbol already in watchlist'}), 400
        
        # Add to watchlist
        cursor.execute(
            'INSERT INTO watchlist (symbol, name, market) VALUES (?, ?, ?)',
            (symbol, name, market)
        )
        
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success', 'message': f'{symbol} added to watchlist'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@symbol_bp.route('/api/watchlist/remove', methods=['POST'])
def remove_from_watchlist():
    """API endpoint to remove a symbol from the watchlist"""
    try:
        data = request.get_json()
        
        if not data or 'symbol' not in data:
            return jsonify({'status': 'error', 'message': 'Symbol is required'}), 400
        
        symbol = data['symbol']
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Remove from watchlist
        cursor.execute('DELETE FROM watchlist WHERE symbol = ?', (symbol,))
        
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success', 'message': f'{symbol} removed from watchlist'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@symbol_bp.route('/api/watchlist/save', methods=['POST'])
def save_watchlist():
    """API endpoint to save the watchlist to trading_config.json"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT symbol FROM watchlist')
        rows = cursor.fetchall()
        
        symbols = [row['symbol'] for row in rows]
        
        # Read existing config
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'config', 'trading_config.json')
        
        if os.path.exists(config_path):
            with open(config_path, 'r') as f:
                config = json.load(f)
        else:
            config = {
                "max_positions": 8,
                "position_size_pct": 0.1,
                "stop_loss_pct": 0.05,
                "take_profit_pct": 0.15,
                "daily_loss_limit": 0.02,
                "max_trades_per_day": 10
            }
        
        # Update symbols
        config['symbols'] = symbols
        
        # Write back to config
        with open(config_path, 'w') as f:
            json.dump(config, f, indent=2)
        
        conn.close()
        
        return jsonify({'status': 'success', 'message': 'Watchlist saved to trading configuration'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500