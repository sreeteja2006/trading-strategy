#!/usr/bin/env python3
"""
Paper Trading System - Test your strategy with virtual money
"""
import sys
sys.path.append('scripts')

import pandas as pd
import yfinance as yf
from datetime import datetime, timedelta
import json
import os

class PaperTradingAccount:
    def __init__(self, initial_balance=100000):
        self.initial_balance = initial_balance
        self.balance = initial_balance
        self.positions = {}  # {symbol: {'shares': int, 'avg_price': float}}
        self.transactions = []
        self.portfolio_value_history = []
        
    def get_current_price(self, symbol):
        """Get current market price"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")
            return data['Close'].iloc[-1] if not data.empty else None
        except:
            return None
    
    def buy_stock(self, symbol, shares, price=None):
        """Execute buy order"""
        if price is None:
            price = self.get_current_price(symbol)
            
        if price is None:
            return False, "Could not get current price"
            
        total_cost = shares * price
        
        if total_cost > self.balance:
            return False, f"Insufficient funds. Need ₹{total_cost:.2f}, have ₹{self.balance:.2f}"
        
        # Execute trade
        self.balance -= total_cost
        
        if symbol in self.positions:
            # Update average price
            current_shares = self.positions[symbol]['shares']
            current_avg = self.positions[symbol]['avg_price']
            new_avg = ((current_shares * current_avg) + (shares * price)) / (current_shares + shares)
            
            self.positions[symbol]['shares'] += shares
            self.positions[symbol]['avg_price'] = new_avg
        else:
            self.positions[symbol] = {'shares': shares, 'avg_price': price}
        
        # Record transaction
        self.transactions.append({
            'timestamp': datetime.now(),
            'action': 'BUY',
            'symbol': symbol,
            'shares': shares,
            'price': price,
            'total': total_cost,
            'balance_after': self.balance
        })
        
        return True, f"Bought {shares} shares of {symbol} at ₹{price:.2f}"
    
    def sell_stock(self, symbol, shares, price=None):
        """Execute sell order"""
        if symbol not in self.positions:
            return False, f"No position in {symbol}"
            
        if self.positions[symbol]['shares'] < shares:
            return False, f"Insufficient shares. Have {self.positions[symbol]['shares']}, trying to sell {shares}"
        
        if price is None:
            price = self.get_current_price(symbol)
            
        if price is None:
            return False, "Could not get current price"
        
        # Execute trade
        total_proceeds = shares * price
        self.balance += total_proceeds
        
        self.positions[symbol]['shares'] -= shares
        
        # Remove position if no shares left
        if self.positions[symbol]['shares'] == 0:
            del self.positions[symbol]
        
        # Record transaction
        self.transactions.append({
            'timestamp': datetime.now(),
            'action': 'SELL',
            'symbol': symbol,
            'shares': shares,
            'price': price,
            'total': total_proceeds,
            'balance_after': self.balance
        })
        
        return True, f"Sold {shares} shares of {symbol} at ₹{price:.2f}"
    
    def get_portfolio_value(self):
        """Calculate total portfolio value"""
        total_value = self.balance
        
        for symbol, position in self.positions.items():
            current_price = self.get_current_price(symbol)
            if current_price:
                total_value += position['shares'] * current_price
        
        return total_value
    
    def get_portfolio_summary(self):
        """Get detailed portfolio summary"""
        summary = {
            'cash_balance': self.balance,
            'positions': {},
            'total_portfolio_value': 0,
            'total_return': 0,
            'total_return_pct': 0
        }
        
        position_value = 0
        
        for symbol, position in self.positions.items():
            current_price = self.get_current_price(symbol)
            if current_price:
                market_value = position['shares'] * current_price
                cost_basis = position['shares'] * position['avg_price']
                pnl = market_value - cost_basis
                pnl_pct = (pnl / cost_basis) * 100 if cost_basis > 0 else 0
                
                summary['positions'][symbol] = {
                    'shares': position['shares'],
                    'avg_price': position['avg_price'],
                    'current_price': current_price,
                    'market_value': market_value,
                    'cost_basis': cost_basis,
                    'pnl': pnl,
                    'pnl_pct': pnl_pct
                }
                
                position_value += market_value
        
        summary['total_portfolio_value'] = self.balance + position_value
        summary['total_return'] = summary['total_portfolio_value'] - self.initial_balance
        summary['total_return_pct'] = (summary['total_return'] / self.initial_balance) * 100
        
        return summary
    
    def save_account(self, filename='paper_trading_account.json'):
        """Save account state to file"""
        account_data = {
            'initial_balance': self.initial_balance,
            'balance': self.balance,
            'positions': self.positions,
            'transactions': [
                {**t, 'timestamp': t['timestamp'].isoformat()} 
                for t in self.transactions
            ]
        }
        
        with open(filename, 'w') as f:
            json.dump(account_data, f, indent=2)
    
    def load_account(self, filename='paper_trading_account.json'):
        """Load account state from file"""
        if not os.path.exists(filename):
            return False
            
        with open(filename, 'r') as f:
            account_data = json.load(f)
        
        self.initial_balance = account_data['initial_balance']
        self.balance = account_data['balance']
        self.positions = account_data['positions']
        self.transactions = [
            {**t, 'timestamp': datetime.fromisoformat(t['timestamp'])} 
            for t in account_data['transactions']
        ]
        
        return True

def run_paper_trading_demo():
    """Demo of paper trading system"""
    print("🎯 Paper Trading System Demo")
    print("=" * 50)
    
    # Create account
    account = PaperTradingAccount(initial_balance=100000)
    
    # Try to load existing account
    if account.load_account():
        print("📂 Loaded existing account")
    else:
        print("🆕 Created new account")
    
    print(f"💰 Starting Balance: ₹{account.balance:,.2f}")
    
    # Demo trades
    symbols = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS']
    
    for symbol in symbols:
        print(f"\n📊 Testing {symbol}...")
        
        # Get current price
        price = account.get_current_price(symbol)
        if price:
            print(f"Current price: ₹{price:.2f}")
            
            # Buy some shares
            shares_to_buy = 10
            success, message = account.buy_stock(symbol, shares_to_buy)
            print(f"Buy order: {message}")
            
        else:
            print(f"❌ Could not get price for {symbol}")
    
    # Show portfolio summary
    print("\n📈 Portfolio Summary:")
    print("=" * 30)
    summary = account.get_portfolio_summary()
    
    print(f"Cash Balance: ₹{summary['cash_balance']:,.2f}")
    print(f"Total Portfolio Value: ₹{summary['total_portfolio_value']:,.2f}")
    print(f"Total Return: ₹{summary['total_return']:,.2f} ({summary['total_return_pct']:+.2f}%)")
    
    print("\n📋 Positions:")
    for symbol, pos in summary['positions'].items():
        print(f"{symbol}: {pos['shares']} shares @ ₹{pos['avg_price']:.2f} "
              f"(Current: ₹{pos['current_price']:.2f}, P&L: ₹{pos['pnl']:+.2f})")
    
    # Show recent transactions
    print("\n📝 Recent Transactions:")
    for transaction in account.transactions[-5:]:
        print(f"{transaction['timestamp'].strftime('%Y-%m-%d %H:%M')} - "
              f"{transaction['action']} {transaction['shares']} {transaction['symbol']} "
              f"@ ₹{transaction['price']:.2f}")
    
    # Save account
    account.save_account()
    print("\n💾 Account saved!")
    
    return account

if __name__ == "__main__":
    account = run_paper_trading_demo()