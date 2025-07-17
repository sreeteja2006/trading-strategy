#!/usr/bin/env python3
"""
Flask Web Application for Trading System
"""
from flask import Flask, render_template, jsonify, request, redirect, url_for
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import plotly.utils
import yfinance as yf
from datetime import datetime, timedelta
import json
import os
import psutil
import random

app = Flask(__name__)

# Create necessary directories
os.makedirs('data', exist_ok=True)
os.makedirs('data/processed', exist_ok=True)
os.makedirs('data/raw', exist_ok=True)
os.makedirs('data/results', exist_ok=True)
os.makedirs('logs', exist_ok=True)

# Import blueprints
from apps.symbol_manager import symbol_bp

# Register blueprints
app.register_blueprint(symbol_bp)

# Mock data for demo
PORTFOLIO_DATA = {
    'RELIANCE': {'shares': 100, 'avg_price': 2450, 'current_price': 2475, 'pnl': 2500, 'market_value': 247500, 'pnl_pct': 1.02},
    'TCS': {'shares': 50, 'avg_price': 3500, 'current_price': 3560, 'pnl': 3000, 'market_value': 178000, 'pnl_pct': 1.71},
    'INFY': {'shares': 200, 'avg_price': 1800, 'current_price': 1825, 'pnl': 5000, 'market_value': 365000, 'pnl_pct': 1.39}
}

@app.route('/')
def home():
    """Home page with system overview"""
    total_value = sum(pos['market_value'] for pos in PORTFOLIO_DATA.values())
    total_pnl = sum(pos['pnl'] for pos in PORTFOLIO_DATA.values())
    
    stats = {
        'portfolio_value': total_value,
        'total_pnl': total_pnl,
        'cash_balance': 250000,
        'active_positions': len(PORTFOLIO_DATA),
        'today_trades': 12,
        'system_uptime': '99.8%'
    }
    
    return render_template('home.html', stats=stats)

@app.route('/dashboard')
def dashboard():
    """Trading dashboard with charts"""
    # Get watchlist symbols for the dropdown
    try:
        from apps.symbol_manager import get_db_connection
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('SELECT symbol, name FROM watchlist ORDER BY added_date DESC')
        watchlist_symbols = cursor.fetchall()
        conn.close()
        
        # Convert to list of dictionaries
        symbols = [{'symbol': row['symbol'], 'name': row['name']} for row in watchlist_symbols]
        
        # If no symbols in watchlist, provide default ones
        if not symbols:
            symbols = [
                {'symbol': 'RELIANCE.NS', 'name': 'Reliance Industries'},
                {'symbol': 'TCS.NS', 'name': 'TCS'},
                {'symbol': 'INFY.NS', 'name': 'Infosys'},
                {'symbol': 'HDFCBANK.NS', 'name': 'HDFC Bank'}
            ]
    except Exception as e:
        print(f"Error loading watchlist: {e}")
        # Fallback to default symbols
        symbols = [
            {'symbol': 'RELIANCE.NS', 'name': 'Reliance Industries'},
            {'symbol': 'TCS.NS', 'name': 'TCS'},
            {'symbol': 'INFY.NS', 'name': 'Infosys'},
            {'symbol': 'HDFCBANK.NS', 'name': 'HDFC Bank'}
        ]
    
    # Get the selected symbol from query parameters, or use the first symbol from watchlist
    selected_symbol = request.args.get('symbol')
    if not selected_symbol and symbols:
        selected_symbol = symbols[0]['symbol']
    
    return render_template('dashboard.html', symbols=symbols, selected_symbol=selected_symbol)

@app.route('/performance')
def performance():
    """Performance tracking dashboard"""
    # Mock portfolio summary
    summary = {
        'total_portfolio_value': 1250000,
        'total_return': 50000,
        'total_return_pct': 4.17,
        'cash_balance': 250000,
        'positions': PORTFOLIO_DATA
    }
    
    return render_template('performance.html', summary=summary)

@app.route('/system')
def system():
    """System status dashboard"""
    # Get system metrics
    metrics = {
        "cpu_percent": psutil.cpu_percent(),
        "memory_percent": psutil.virtual_memory().percent,
        "disk_percent": psutil.disk_usage('/').percent,
        "boot_time": datetime.fromtimestamp(psutil.boot_time()).strftime("%Y-%m-%d %H:%M:%S"),
        "uptime_hours": (datetime.now() - datetime.fromtimestamp(psutil.boot_time())).total_seconds() / 3600
    }
    
    # Mock resource data
    timestamps = [datetime.now() - timedelta(minutes=i*5) for i in range(12)]
    timestamps.reverse()
    
    cpu_values = [metrics['cpu_percent'] - 10 + i*2 for i in range(12)]
    cpu_values = [max(0, min(100, x)) for x in cpu_values]
    
    memory_values = [metrics['memory_percent'] - 5 + i for i in range(12)]
    memory_values = [max(0, min(100, x)) for x in memory_values]
    
    resource_data = {
        'timestamps': [t.strftime('%H:%M') for t in timestamps],
        'cpu': cpu_values,
        'memory': memory_values
    }
    
    # Mock services
    services = {
        'web': True,
        'data': True,
        'trading': True
    }
    
    return render_template(
        'system.html',
        metrics=metrics,
        resource_data=json.dumps(resource_data),
        containers=[],
        services=services,
        last_updated=datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    )

@app.route('/trading')
def trading():
    """Trading interface"""
    return render_template('trading.html')

@app.route('/api/stock_data/<symbol>')
def get_stock_data(symbol):
    """API endpoint to get stock data"""
    try:
        print(f"Fetching real data for symbol: {symbol}")
        
        # Handle Indian stocks with .NS suffix
        if symbol.endswith('.NS'):
            # For Indian stocks, we need to use the Yahoo Finance format without the exchange suffix
            clean_symbol = symbol.split('.')[0] + ".NS"
            # Special handling for known Indian stocks
            if clean_symbol == "RELIANCE.NS":
                clean_symbol = "RELIANCE.NS"
            elif clean_symbol == "TCS.NS":
                clean_symbol = "TCS.NS"
            elif clean_symbol == "INFY.NS":
                clean_symbol = "INFY.NS"
            elif clean_symbol == "HDFCBANK.NS":
                clean_symbol = "HDFCBANK.NS"
        else:
            # For other stocks, remove any exchange suffixes
            clean_symbol = symbol.split('.')[0]
        
        # Get the ticker object
        ticker = yf.Ticker(clean_symbol)
        
        # Try to fetch data with a 1-month period first
        try:
            data = yf.download(
                clean_symbol, 
                period="1mo",
                progress=False
            )
            if data.empty:
                raise ValueError("Empty data returned")
        except:
            # If 1mo fails, try 3mo
            try:
                data = yf.download(
                    clean_symbol, 
                    period="3mo",
                    progress=False
                )
                if data.empty:
                    raise ValueError("Empty data returned")
            except:
                # If 3mo fails, try 6mo
                try:
                    data = yf.download(
                        clean_symbol, 
                        period="6mo",
                        progress=False
                    )
                    if data.empty:
                        raise ValueError("Empty data returned")
                except:
                    # Final fallback to 1y
                    data = yf.download(
                        clean_symbol, 
                        period="1y",
                        progress=False
                    )
        
        if data.empty:
            return jsonify({
                'error': f'No data available for {symbol}. '
                         f'Please check the symbol or try a different one.'
            })
        
        # Ensure we have at least 2 days of data for change calculation
        if len(data) < 2:
            return jsonify({
                'error': f'Insufficient data for {symbol} '
                         f'(only {len(data)} days available)'
            })
        
        # Get current quote for accurate pricing
        try:
            # First try to get real-time data
            current_info = ticker.fast_info
            current_price = current_info.last_price
            
            # If real-time price is not available, use the last close
            if current_price is None:
                current_price = data['Close'].iloc[-1]
            
            # Try to get previous close
            prev_close = current_info.previous_close
            if prev_close is None:
                prev_close = data['Close'].iloc[-2]
        except:
            # Fallback to historical data if real-time fails
            current_price = data['Close'].iloc[-1]
            prev_close = data['Close'].iloc[-2]
        
        # Calculate change
        change = current_price - prev_close
        change_pct = (change / prev_close) * 100
        
        # Convert to JSON format
        chart_data = {
            'dates': data.index.strftime('%Y-%m-%d').tolist(),
            'open': data['Open'].tolist(),
            'high': data['High'].tolist(),
            'low': data['Low'].tolist(),
            'close': data['Close'].tolist(),
            'volume': data['Volume'].tolist(),
            'current_price': float(current_price),
            'change': float(change),
            'change_pct': float(change_pct)
        }
        
        print(f"Successfully prepared real chart data for {clean_symbol}")
        return jsonify(chart_data)
        
    except Exception as e:
        error_msg = f"Error fetching data for {symbol}: {str(e)}"
        print(error_msg)
        return jsonify({'error': error_msg})

@app.route('/api/portfolio')
def get_portfolio():
    """API endpoint to get portfolio data"""
    portfolio_list = []
    for symbol, pos in PORTFOLIO_DATA.items():
        portfolio_list.append({
            'symbol': symbol,
            'shares': pos['shares'],
            'avg_price': pos['avg_price'],
            'current_price': pos['current_price'],
            'market_value': pos['market_value'],
            'pnl': pos['pnl'],
            'pnl_pct': pos['pnl_pct']
        })
    
    return jsonify(portfolio_list)

@app.route('/api/system_status')
def system_status():
    """API endpoint for system status"""
    status = {
        'timestamp': datetime.now().isoformat(),
        'status': 'online',
        'cpu_usage': psutil.cpu_percent(),
        'memory_usage': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent,
        'uptime': '24h 15m'
    }
    
    return jsonify(status)

@app.route('/system/api/logs')
def get_logs():
    """API endpoint to get logs"""
    service = request.args.get('service', 'all')
    lines = request.args.get('lines', 10, type=int)
    
    # Mock log data
    log_data = f"Sample log data for {service}\n"
    log_data += "2025-07-17 10:15:23 INFO  Server started\n"
    log_data += "2025-07-17 10:15:24 INFO  Connected to database\n"
    log_data += "2025-07-17 10:15:25 INFO  Loaded configuration\n"
    log_data += "2025-07-17 10:16:30 INFO  User login: admin\n"
    log_data += "2025-07-17 10:17:45 INFO  API request: /api/portfolio\n"
    
    return jsonify({'status': 'success', 'logs': log_data})

@app.route('/system/api/restart', methods=['POST'])
def restart_services():
    """API endpoint to restart services"""
    return jsonify({'status': 'success', 'message': 'Services restarted successfully'})

@app.route('/system/api/backup', methods=['POST'])
def create_backup():
    """API endpoint to create a backup"""
    backup_time = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_file = f"backup_{backup_time}.tar.gz"
    
    return jsonify({
        'status': 'success', 
        'message': f'Backup created: {backup_file}',
        'file': backup_file
    })

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({'status': 'healthy'})

@app.route('/api/search_symbols/<query>')
def search_symbols(query):
    """Search for stock symbols by company name"""
    try:
        search_results = yf.Ticker(query).info
        results = [{
            'symbol': search_results.get('symbol', query),
            'name': search_results.get('shortName', query),
            'exchange': search_results.get('exchange', 'N/A')
        }]
        return jsonify(results)
    except:
        return jsonify([])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)