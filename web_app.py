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

app = Flask(__name__)

# Mock data for demo
PORTFOLIO_DATA = {
    'RELIANCE': {'shares': 100, 'avg_price': 2450, 'current_price': 2475, 'pnl': 2500, 'market_value': 247500, 'pnl_pct': 1.02},
    'TCS': {'shares': 50, 'avg_price': 3500, 'current_price': 3560, 'pnl': 3000, 'market_value': 178000, 'pnl_pct': 1.71},
    'INFY': {'shares': 200, 'avg_price': 1800, 'current_price': 1825, 'pnl': 5000, 'market_value': 365000, 'pnl_pct': 1.39}
}

@app.route('/')
def home():
    """Home page with system overview"""
    total_value = sum(pos['shares'] * pos['current_price'] for pos in PORTFOLIO_DATA.values())
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
    return render_template('dashboard.html')

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

@app.route('/trading')
def trading():
    """Trading interface"""
    return render_template('trading.html')

@app.route('/api/stock_data/<symbol>')
def get_stock_data(symbol):
    """API endpoint to get stock data"""
    try:
        ticker = yf.Ticker(f"{symbol}.NS")
        data = ticker.history(period="30d")
        
        if data.empty:
            return jsonify({'error': 'No data available'})
        
        # Convert to JSON format
        chart_data = {
            'dates': data.index.strftime('%Y-%m-%d').tolist(),
            'open': data['Open'].tolist(),
            'high': data['High'].tolist(),
            'low': data['Low'].tolist(),
            'close': data['Close'].tolist(),
            'volume': data['Volume'].tolist(),
            'current_price': float(data['Close'].iloc[-1]),
            'change': float(data['Close'].iloc[-1] - data['Close'].iloc[-2]),
            'change_pct': float((data['Close'].iloc[-1] - data['Close'].iloc[-2]) / data['Close'].iloc[-2] * 100)
        }
        
        return jsonify(chart_data)
    except Exception as e:
        return jsonify({'error': str(e)})

@app.route('/api/execute_trade', methods=['POST'])
def execute_trade():
    """API endpoint to execute trades"""
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        action = data.get('action')
        quantity = int(data.get('quantity', 0))
        
        # Simulate trade execution
        result = {
            'status': 'success',
            'message': f'{action} order for {quantity} shares of {symbol} executed successfully',
            'timestamp': datetime.now().isoformat(),
            'order_id': f'ORD{datetime.now().strftime("%Y%m%d%H%M%S")}'
        }
        
        return jsonify(result)
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/portfolio')
def get_portfolio():
    """API endpoint to get portfolio data"""
    portfolio_list = []
    for symbol, pos in PORTFOLIO_DATA.items():
        market_value = pos['shares'] * pos['current_price']
        pnl_pct = (pos['pnl'] / (pos['shares'] * pos['avg_price'])) * 100
        
        portfolio_list.append({
            'symbol': symbol,
            'shares': pos['shares'],
            'avg_price': pos['avg_price'],
            'current_price': pos['current_price'],
            'market_value': market_value,
            'pnl': pos['pnl'],
            'pnl_pct': pnl_pct
        })
    
    return jsonify(portfolio_list)

@app.route('/api/system_status')
def system_status():
    """API endpoint for system status"""
    import psutil
    
    status = {
        'timestamp': datetime.now().isoformat(),
        'status': 'online',
        'cpu_usage': psutil.cpu_percent(),
        'memory_usage': psutil.virtual_memory().percent,
        'disk_usage': psutil.disk_usage('/').percent,
        'uptime': '24h 15m'
    }
    
    return jsonify(status)

@app.route('/health')
def health_check():
    """Health check endpoint for Render"""
    return jsonify({'status': 'healthy'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)