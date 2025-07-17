#!/usr/bin/env python3
"""
Performance Dashboard - Track your trading strategy results
"""
from flask import Blueprint, render_template, jsonify, request
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import sqlite3
import pathlib

# Create a blueprint for the performance dashboard
performance_bp = Blueprint('performance', __name__, url_prefix='/performance')

# Database setup
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'trading.db')
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
    
    # Create positions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS positions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        shares INTEGER NOT NULL,
        avg_price REAL NOT NULL,
        current_price REAL NOT NULL,
        last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create transactions table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        time TEXT NOT NULL,
        action TEXT NOT NULL,
        symbol TEXT NOT NULL,
        shares INTEGER NOT NULL,
        price REAL NOT NULL,
        total REAL NOT NULL,
        balance_after REAL NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    # Create portfolio_history table
    cursor.execute('''
    CREATE TABLE IF NOT EXISTS portfolio_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT NOT NULL,
        portfolio_value REAL NOT NULL,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

# Initialize the database
init_db()

def get_portfolio_summary():
    """Get portfolio summary from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get positions
    cursor.execute('SELECT * FROM positions')
    positions_rows = cursor.fetchall()
    
    positions = {}
    total_market_value = 0
    
    for row in positions_rows:
        market_value = row['shares'] * row['current_price']
        pnl = (row['current_price'] - row['avg_price']) * row['shares']
        pnl_pct = (row['current_price'] - row['avg_price']) / row['avg_price'] * 100
        
        positions[row['symbol']] = {
            'shares': row['shares'],
            'avg_price': row['avg_price'],
            'current_price': row['current_price'],
            'market_value': market_value,
            'pnl': pnl,
            'pnl_pct': pnl_pct
        }
        
        total_market_value += market_value
    
    # If no positions exist, add sample data
    if not positions:
        sample_positions = {
            'RELIANCE': {'shares': 100, 'avg_price': 2450, 'current_price': 2475},
            'TCS': {'shares': 50, 'avg_price': 3500, 'current_price': 3560},
            'INFY': {'shares': 200, 'avg_price': 1800, 'current_price': 1825}
        }
        
        for symbol, data in sample_positions.items():
            market_value = data['shares'] * data['current_price']
            pnl = (data['current_price'] - data['avg_price']) * data['shares']
            pnl_pct = (data['current_price'] - data['avg_price']) / data['avg_price'] * 100
            
            positions[symbol] = {
                'shares': data['shares'],
                'avg_price': data['avg_price'],
                'current_price': data['current_price'],
                'market_value': market_value,
                'pnl': pnl,
                'pnl_pct': pnl_pct
            }
            
            total_market_value += market_value
    
    # Get cash balance (for demo, we'll use a fixed value if not in DB)
    cash_balance = 250000
    total_portfolio_value = total_market_value + cash_balance
    initial_investment = 1200000  # For demo purposes
    total_return = total_portfolio_value - initial_investment
    total_return_pct = (total_return / initial_investment) * 100
    
    summary = {
        'total_portfolio_value': total_portfolio_value,
        'total_return': total_return,
        'total_return_pct': total_return_pct,
        'cash_balance': cash_balance,
        'positions': positions
    }
    
    conn.close()
    return summary

def get_transactions():
    """Get recent transactions from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get transactions
    cursor.execute('SELECT * FROM transactions ORDER BY date DESC, time DESC LIMIT 10')
    transactions_rows = cursor.fetchall()
    
    transactions = []
    for row in transactions_rows:
        transactions.append({
            'Date': row['date'],
            'Time': row['time'],
            'Action': row['action'],
            'Symbol': row['symbol'],
            'Shares': row['shares'],
            'Price': f"₹{row['price']:,.2f}",
            'Total': f"₹{row['total']:,.2f}",
            'Balance After': f"₹{row['balance_after']:,.2f}"
        })
    
    # If no transactions exist, add sample data
    if not transactions:
        transactions = [
            {'Date': '2025-01-17', 'Time': '09:15:00', 'Action': 'BUY', 'Symbol': 'RELIANCE', 'Shares': 100, 'Price': '₹2,450.00', 'Total': '₹2,45,000', 'Balance After': '₹7,55,000'},
            {'Date': '2025-01-16', 'Time': '14:30:00', 'Action': 'BUY', 'Symbol': 'TCS', 'Shares': 50, 'Price': '₹3,500.00', 'Total': '₹1,75,000', 'Balance After': '₹10,00,000'},
            {'Date': '2025-01-15', 'Time': '11:45:00', 'Action': 'SELL', 'Symbol': 'INFY', 'Shares': 25, 'Price': '₹1,820.00', 'Total': '₹45,500', 'Balance After': '₹11,75,000'},
            {'Date': '2025-01-14', 'Time': '10:20:00', 'Action': 'BUY', 'Symbol': 'INFY', 'Shares': 200, 'Price': '₹1,800.00', 'Total': '₹3,60,000', 'Balance After': '₹11,30,000'}
        ]
    
    conn.close()
    return transactions

def get_performance_history():
    """Get portfolio performance history from database"""
    conn = get_db_connection()
    cursor = conn.cursor()
    
    # Get portfolio history
    cursor.execute('SELECT * FROM portfolio_history ORDER BY date ASC')
    history_rows = cursor.fetchall()
    
    dates = []
    values = []
    
    for row in history_rows:
        dates.append(row['date'])
        values.append(row['portfolio_value'])
    
    # If no history exists, create sample data
    if not dates:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30)
        dates = [(start_date + timedelta(days=i)).strftime('%Y-%m-%d') for i in range(31)]
        
        initial_value = 1200000
        values = []
        current_value = initial_value
        
        for i in range(31):
            # Add some random fluctuation
            change = current_value * (0.005 * (0.5 - float(os.urandom(1)[0]) / 255.0))
            current_value += change
            values.append(current_value)
    
    conn.close()
    return {'dates': dates, 'values': values}

@performance_bp.route('/')
def performance_dashboard():
    """Render the performance dashboard"""
    summary = get_portfolio_summary()
    transactions = get_transactions()
    performance_data = get_performance_history()
    
    # Strategy statistics (for demo purposes)
    stats = {
        'win_rate': '65%',
        'avg_return': '+2.3%',
        'best_trade': '+₹1,250',
        'worst_trade': '-₹850',
        'sharpe_ratio': '1.45',
        'max_drawdown': '-3.2%'
    }
    
    return render_template(
        'performance.html',
        summary=summary,
        transactions=transactions,
        performance_data=json.dumps(performance_data),
        stats=stats,
        is_demo=True
    )

@performance_bp.route('/api/data')
def get_performance_data():
    """API endpoint for performance data"""
    summary = get_portfolio_summary()
    return jsonify(summary)

@performance_bp.route('/api/update_position', methods=['POST'])
def update_position():
    """API endpoint to update a position"""
    try:
        data = request.get_json()
        symbol = data.get('symbol')
        shares = int(data.get('shares', 0))
        avg_price = float(data.get('avg_price', 0))
        current_price = float(data.get('current_price', 0))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if position exists
        cursor.execute('SELECT * FROM positions WHERE symbol = ?', (symbol,))
        position = cursor.fetchone()
        
        if position:
            # Update existing position
            cursor.execute('''
                UPDATE positions 
                SET shares = ?, avg_price = ?, current_price = ?, last_updated = CURRENT_TIMESTAMP
                WHERE symbol = ?
            ''', (shares, avg_price, current_price, symbol))
        else:
            # Insert new position
            cursor.execute('''
                INSERT INTO positions (symbol, shares, avg_price, current_price)
                VALUES (?, ?, ?, ?)
            ''', (symbol, shares, avg_price, current_price))
        
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success', 'message': f'Position for {symbol} updated successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500

@performance_bp.route('/api/add_transaction', methods=['POST'])
def add_transaction():
    """API endpoint to add a transaction"""
    try:
        data = request.get_json()
        date = data.get('date', datetime.now().strftime('%Y-%m-%d'))
        time = data.get('time', datetime.now().strftime('%H:%M:%S'))
        action = data.get('action')
        symbol = data.get('symbol')
        shares = int(data.get('shares', 0))
        price = float(data.get('price', 0))
        total = price * shares
        balance_after = float(data.get('balance_after', 0))
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO transactions (date, time, action, symbol, shares, price, total, balance_after)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (date, time, action, symbol, shares, price, total, balance_after))
        
        conn.commit()
        conn.close()
        
        return jsonify({'status': 'success', 'message': 'Transaction added successfully'})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500