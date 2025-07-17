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
import requests
import pandas as pd

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
        results = []
        
        # First approach: Use Yahoo Finance API directly
        try:
            url = f"https://query2.finance.yahoo.com/v1/finance/search?q={query}&quotesCount=20&newsCount=0"
            headers = {'User-Agent': 'Mozilla/5.0'}
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                data = response.json()
                if 'quotes' in data and data['quotes']:
                    for quote in data['quotes']:
                        if 'symbol' in quote:
                            market_type = get_market_type_from_quote(quote)
                            
                            if market == 'all' or market.lower() == market_type.lower():
                                # Get current price
                                price = None
                                change = None
                                try:
                                    ticker = yf.Ticker(quote['symbol'])
                                    hist = ticker.history(period='2d')
                                    if not hist.empty:
                                        price = hist['Close'].iloc[-1]
                                        if len(hist) > 1:
                                            prev_close = hist['Close'].iloc[-2]
                                            change = ((price - prev_close) / prev_close) * 100
                                except:
                                    pass
                                
                                results.append({
                                    'symbol': quote['symbol'],
                                    'name': quote.get('shortname', quote.get('longname', 'Unknown')),
                                    'market': market_type,
                                    'price': price,
                                    'change': change
                                })
        except Exception as e:
            print(f"Yahoo Finance API search error: {str(e)}")
        
        # Second approach: Try direct symbol lookup if first approach didn't yield results
        if not results:
            try:
                # Try exact symbol match
                ticker = yf.Ticker(query)
                info = ticker.info
                
                if info and 'symbol' in info:
                    market_type = get_market_type(info)
                    
                    if market == 'all' or market.lower() == market_type.lower():
                        results.append({
                            'symbol': info['symbol'],
                            'name': info.get('longName', info.get('shortName', 'Unknown')),
                            'market': market_type,
                            'price': info.get('regularMarketPrice', None),
                            'change': info.get('regularMarketChangePercent', None)
                        })
            except Exception as e:
                print(f"Direct symbol lookup error: {str(e)}")
        
        # Third approach: Use a comprehensive list of common symbols
        if not results:
            # Load symbol lists from files if they exist, otherwise use a smaller default list
            symbols_data = load_symbol_lists()
            
            query_upper = query.upper()
            query_lower = query.lower()
            
            for symbol, data in symbols_data.items():
                if (query_upper in symbol) or (query_lower in data['name'].lower()):
                    if market == 'all' or market.lower() == data['market'].lower():
                        # Try to get current price
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
                        
                        results.append({
                            'symbol': symbol,
                            'name': data['name'],
                            'market': data['market'],
                            'price': price,
                            'change': change
                        })
                        
                        # Limit to 20 results for performance
                        if len(results) >= 20:
                            break
        
        return jsonify({'status': 'success', 'data': results})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

def get_market_type_from_quote(quote):
    """Determine market type from Yahoo Finance quote"""
    if 'quoteType' in quote:
        quote_type = quote['quoteType']
        if quote_type == 'EQUITY':
            return 'Stocks'
        elif quote_type == 'ETF':
            return 'ETFs'
        elif quote_type == 'INDEX':
            return 'Indices'
        elif quote_type in ['CURRENCY', 'CRYPTOCURRENCY']:
            return 'Forex'
        elif quote_type == 'FUTURE':
            return 'Commodities'
    
    # Try to determine from exchange
    if 'exchange' in quote:
        exchange = quote['exchange'].upper()
        if exchange in ['MCX', 'NYMEX', 'COMEX']:
            return 'Commodities'
    
    # Default to stocks
    return 'Stocks'

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

def load_symbol_lists():
    """Load comprehensive symbol lists"""
    symbols_data = {}
    
    # Default symbols (minimal set)
    default_symbols = {
        # Indian Stocks
        'RELIANCE.NS': {'name': 'Reliance Industries Ltd', 'market': 'Stocks'},
        'TCS.NS': {'name': 'Tata Consultancy Services Ltd', 'market': 'Stocks'},
        'INFY.NS': {'name': 'Infosys Ltd', 'market': 'Stocks'},
        'HDFCBANK.NS': {'name': 'HDFC Bank Ltd', 'market': 'Stocks'},
        'ICICIBANK.NS': {'name': 'ICICI Bank Ltd', 'market': 'Stocks'},
        'SBIN.NS': {'name': 'State Bank of India', 'market': 'Stocks'},
        'HINDUNILVR.NS': {'name': 'Hindustan Unilever Ltd', 'market': 'Stocks'},
        'BHARTIARTL.NS': {'name': 'Bharti Airtel Ltd', 'market': 'Stocks'},
        'ITC.NS': {'name': 'ITC Ltd', 'market': 'Stocks'},
        'KOTAKBANK.NS': {'name': 'Kotak Mahindra Bank Ltd', 'market': 'Stocks'},
        
        # US Stocks
        'AAPL': {'name': 'Apple Inc', 'market': 'Stocks'},
        'MSFT': {'name': 'Microsoft Corporation', 'market': 'Stocks'},
        'GOOGL': {'name': 'Alphabet Inc', 'market': 'Stocks'},
        'AMZN': {'name': 'Amazon.com Inc', 'market': 'Stocks'},
        'META': {'name': 'Meta Platforms Inc', 'market': 'Stocks'},
        'TSLA': {'name': 'Tesla Inc', 'market': 'Stocks'},
        'NVDA': {'name': 'NVIDIA Corporation', 'market': 'Stocks'},
        'JPM': {'name': 'JPMorgan Chase & Co', 'market': 'Stocks'},
        'V': {'name': 'Visa Inc', 'market': 'Stocks'},
        'JNJ': {'name': 'Johnson & Johnson', 'market': 'Stocks'},
        
        # Nifty Indices
        '^NSEI': {'name': 'Nifty 50 Index', 'market': 'Indices'},
        '^NSEBANK': {'name': 'Nifty Bank Index', 'market': 'Indices'},
        'NIFTYMIDCAP.NS': {'name': 'Nifty Midcap 100 Index', 'market': 'Indices'},
        'NIFTYSMALL.NS': {'name': 'Nifty Smallcap 100 Index', 'market': 'Indices'},
        'NIFTYIT.NS': {'name': 'Nifty IT Index', 'market': 'Indices'},
        'NIFTYPHARMA.NS': {'name': 'Nifty Pharma Index', 'market': 'Indices'},
        
        # Commodities
        'GC=F': {'name': 'Gold Futures', 'market': 'Commodities'},
        'SI=F': {'name': 'Silver Futures', 'market': 'Commodities'},
        'CL=F': {'name': 'Crude Oil Futures', 'market': 'Commodities'},
        'NG=F': {'name': 'Natural Gas Futures', 'market': 'Commodities'},
        'HG=F': {'name': 'Copper Futures', 'market': 'Commodities'},
    }
    
    symbols_data.update(default_symbols)
    
    # Try to load NSE stocks
    try:
        nse_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'nse_stocks.csv')
        if os.path.exists(nse_file):
            nse_df = pd.read_csv(nse_file)
            for _, row in nse_df.iterrows():
                symbol = f"{row['Symbol']}.NS"
                symbols_data[symbol] = {
                    'name': row['Company Name'],
                    'market': 'Stocks'
                }
    except Exception as e:
        print(f"Error loading NSE stocks: {str(e)}")
    
    # Try to load BSE stocks
    try:
        bse_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'bse_stocks.csv')
        if os.path.exists(bse_file):
            bse_df = pd.read_csv(bse_file)
            for _, row in bse_df.iterrows():
                symbol = f"{row['Symbol']}.BO"
                symbols_data[symbol] = {
                    'name': row['Company Name'],
                    'market': 'Stocks'
                }
    except Exception as e:
        print(f"Error loading BSE stocks: {str(e)}")
    
    # Try to load US stocks
    try:
        us_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'us_stocks.csv')
        if os.path.exists(us_file):
            us_df = pd.read_csv(us_file)
            for _, row in us_df.iterrows():
                symbol = row['Symbol']
                symbols_data[symbol] = {
                    'name': row['Name'],
                    'market': 'Stocks'
                }
    except Exception as e:
        print(f"Error loading US stocks: {str(e)}")
    
    return symbols_data

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

@symbol_bp.route('/api/download_stock_lists', methods=['POST'])
def download_stock_lists():
    """API endpoint to download comprehensive stock lists"""
    try:
        data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Download NSE stocks
        try:
            nse_url = "https://archives.nseindia.com/content/equities/EQUITY_L.csv"
            nse_df = pd.read_csv(nse_url)
            nse_df = nse_df[['SYMBOL', 'NAME OF COMPANY']]
            nse_df.columns = ['Symbol', 'Company Name']
            nse_df.to_csv(os.path.join(data_dir, 'nse_stocks.csv'), index=False)
        except Exception as e:
            print(f"Error downloading NSE stocks: {str(e)}")
        
        # Download US stocks (S&P 500 as an example)
        try:
            sp500_url = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
            sp500_tables = pd.read_html(sp500_url)
            sp500_df = sp500_tables[0]
            sp500_df = sp500_df[['Symbol', 'Security']]
            sp500_df.columns = ['Symbol', 'Name']
            sp500_df.to_csv(os.path.join(data_dir, 'us_stocks.csv'), index=False)
        except Exception as e:
            print(f"Error downloading US stocks: {str(e)}")
        
        return jsonify({'status': 'success', 'message': 'Stock lists downloaded successfully'})
    
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500