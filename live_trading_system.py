#!/usr/bin/env python3
"""
Live Trading System - Execute real trades with your strategy
"""
import sys
sys.path.append('scripts')

import time
import schedule
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
from broker_integration import BrokerManager
from paper_trading import PaperTradingAccount
import json
import os
from typing import Dict, List

class LiveTradingSystem:
    """Complete live trading system with risk management"""
    
    def __init__(self, broker_type='zerodha', mode='paper'):
        self.broker_type = broker_type
        self.mode = mode  # 'paper' or 'live'
        
        # Initialize broker or paper trading
        if mode == 'live':
            self.broker = BrokerManager(broker_type)
            self.paper_account = None
        else:
            self.broker = None
            self.paper_account = PaperTradingAccount()
            self.paper_account.load_account()
        
        # Trading parameters
        self.symbols = ['RELIANCE', 'TCS', 'INFY', 'HDFCBANK', 'ICICIBANK']
        self.max_positions = 5
        self.position_size_pct = 0.1  # 10% per position
        self.stop_loss_pct = 0.05     # 5% stop loss
        self.take_profit_pct = 0.15   # 15% take profit
        
        # Risk management
        self.daily_loss_limit = 0.02  # 2% daily loss limit
        self.max_trades_per_day = 10
        
        # Tracking
        self.daily_trades = 0
        self.daily_pnl = 0
        self.trade_log = []
        
        # Load configuration
        self.load_config()
    
    def load_config(self):
        """Load trading configuration"""
        config_file = 'trading_config.json'
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
                
            self.symbols = config.get('symbols', self.symbols)
            self.max_positions = config.get('max_positions', self.max_positions)
            self.position_size_pct = config.get('position_size_pct', self.position_size_pct)
            self.stop_loss_pct = config.get('stop_loss_pct', self.stop_loss_pct)
            self.take_profit_pct = config.get('take_profit_pct', self.take_profit_pct)
    
    def save_config(self):
        """Save trading configuration"""
        config = {
            'symbols': self.symbols,
            'max_positions': self.max_positions,
            'position_size_pct': self.position_size_pct,
            'stop_loss_pct': self.stop_loss_pct,
            'take_profit_pct': self.take_profit_pct,
            'daily_loss_limit': self.daily_loss_limit,
            'max_trades_per_day': self.max_trades_per_day
        }
        
        with open('trading_config.json', 'w') as f:
            json.dump(config, f, indent=2)
    
    def initialize_system(self) -> bool:
        """Initialize the trading system"""
        print("🚀 Initializing Live Trading System")
        print("=" * 50)
        
        if self.mode == 'live':
            print("⚠️  LIVE TRADING MODE - Real money will be used!")
            confirm = input("Are you sure you want to continue? (yes/no): ")
            if confirm.lower() != 'yes':
                print("❌ Live trading cancelled")
                return False
            
            # Connect to broker
            if not self.broker.connect():
                print("❌ Failed to connect to broker")
                return False
            
            # Get account info
            account_info = self.broker.get_account_info()
            if 'error' in account_info:
                print(f"❌ Error getting account info: {account_info['error']}")
                return False
            
            print("✅ Connected to live broker account")
            
        else:
            print("📝 PAPER TRADING MODE - Virtual money only")
            summary = self.paper_account.get_portfolio_summary()
            print(f"💰 Paper Account Balance: ₹{summary['total_portfolio_value']:,.2f}")
        
        print(f"📊 Monitoring symbols: {', '.join(self.symbols)}")
        print(f"🎯 Max positions: {self.max_positions}")
        print(f"💼 Position size: {self.position_size_pct:.1%} per trade")
        
        return True
    
    def get_account_balance(self) -> float:
        """Get current account balance"""
        if self.mode == 'live':
            account_info = self.broker.get_account_info()
            funds = account_info.get('funds', {})
            return funds.get('available_cash', 0)
        else:
            return self.paper_account.get_portfolio_value()
    
    def get_current_positions(self) -> Dict:
        """Get current positions"""
        if self.mode == 'live':
            account_info = self.broker.get_account_info()
            return account_info.get('positions', [])
        else:
            summary = self.paper_account.get_portfolio_summary()
            return summary['positions']
    
    def calculate_position_size(self, symbol: str, price: float) -> int:
        """Calculate position size based on risk management"""
        account_balance = self.get_account_balance()
        position_value = account_balance * self.position_size_pct
        shares = int(position_value / price)
        return max(1, shares)
    
    def check_risk_limits(self) -> bool:
        """Check if risk limits are exceeded"""
        # Check daily trade limit
        if self.daily_trades >= self.max_trades_per_day:
            print(f"⚠️  Daily trade limit reached ({self.max_trades_per_day})")
            return False
        
        # Check daily loss limit
        account_balance = self.get_account_balance()
        if self.mode == 'paper':
            initial_balance = self.paper_account.initial_balance
        else:
            initial_balance = account_balance  # You'd track this separately
        
        daily_loss_pct = abs(self.daily_pnl) / initial_balance
        if daily_loss_pct > self.daily_loss_limit:
            print(f"⚠️  Daily loss limit exceeded ({daily_loss_pct:.1%})")
            return False
        
        # Check maximum positions
        current_positions = self.get_current_positions()
        if len(current_positions) >= self.max_positions:
            print(f"⚠️  Maximum positions reached ({self.max_positions})")
            return False
        
        return True
    
    def generate_trading_signal(self, symbol: str) -> Dict:
        """Generate trading signal using simplified strategy"""
        try:
            # Get recent data
            ticker = yf.Ticker(f"{symbol}.NS")
            data = ticker.history(period="30d")
            
            if data.empty:
                return {'signal': 'HOLD', 'confidence': 0, 'reason': 'No data'}
            
            # Calculate technical indicators
            current_price = data['Close'].iloc[-1]
            
            # RSI
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            current_rsi = rsi.iloc[-1]
            
            # Moving averages
            sma_20 = data['Close'].rolling(20).mean().iloc[-1]
            sma_50 = data['Close'].rolling(50).mean().iloc[-1]
            
            # Volume
            avg_volume = data['Volume'].rolling(20).mean().iloc[-1]
            current_volume = data['Volume'].iloc[-1]
            volume_ratio = current_volume / avg_volume
            
            # Generate signal
            signal = 'HOLD'
            confidence = 0
            reasons = []
            
            # Buy conditions
            if (current_rsi < 30 and 
                current_price > sma_20 and 
                sma_20 > sma_50 and 
                volume_ratio > 1.2):
                signal = 'BUY'
                confidence = min(0.8, (30 - current_rsi) / 30 + volume_ratio * 0.2)
                reasons.append(f"RSI oversold ({current_rsi:.1f})")
                reasons.append("Uptrend confirmed")
                reasons.append(f"High volume ({volume_ratio:.1f}x)")
            
            # Sell conditions
            elif (current_rsi > 70 and 
                  current_price < sma_20):
                signal = 'SELL'
                confidence = min(0.8, (current_rsi - 70) / 30)
                reasons.append(f"RSI overbought ({current_rsi:.1f})")
                reasons.append("Price below SMA20")
            
            return {
                'signal': signal,
                'confidence': confidence,
                'current_price': current_price,
                'rsi': current_rsi,
                'sma_20': sma_20,
                'sma_50': sma_50,
                'volume_ratio': volume_ratio,
                'reasons': reasons
            }
            
        except Exception as e:
            return {'signal': 'HOLD', 'confidence': 0, 'reason': f'Error: {str(e)}'}
    
    def execute_trade(self, symbol: str, signal_data: Dict) -> bool:
        """Execute a trade based on signal"""
        signal = signal_data['signal']
        confidence = signal_data['confidence']
        current_price = signal_data['current_price']
        
        if signal == 'HOLD' or confidence < 0.3:
            return False
        
        # Check risk limits
        if not self.check_risk_limits():
            return False
        
        # Calculate position size
        shares = self.calculate_position_size(symbol, current_price)
        
        # Execute trade
        if self.mode == 'live':
            # Live trading
            action = 'BUY' if signal == 'BUY' else 'SELL'
            result = self.broker.place_trade(symbol, shares, action)
            
            if result['status'] == 'success':
                self.log_trade(symbol, action, shares, current_price, confidence, 'LIVE')
                self.daily_trades += 1
                return True
            else:
                print(f"❌ Live trade failed: {result['message']}")
                return False
        
        else:
            # Paper trading
            if signal == 'BUY':
                success, message = self.paper_account.buy_stock(symbol, shares, current_price)
            else:
                success, message = self.paper_account.sell_stock(symbol, shares, current_price)
            
            if success:
                self.log_trade(symbol, signal, shares, current_price, confidence, 'PAPER')
                self.daily_trades += 1
                self.paper_account.save_account()
                return True
            else:
                print(f"❌ Paper trade failed: {message}")
                return False
    
    def log_trade(self, symbol: str, action: str, shares: int, price: float, 
                  confidence: float, mode: str):
        """Log trade execution"""
        trade_log = {
            'timestamp': datetime.now(),
            'symbol': symbol,
            'action': action,
            'shares': shares,
            'price': price,
            'confidence': confidence,
            'mode': mode,
            'total_value': shares * price
        }
        
        self.trade_log.append(trade_log)
        
        print(f"✅ {mode} TRADE: {action} {shares} {symbol} @ ₹{price:.2f} "
              f"(Confidence: {confidence:.1%})")
    
    def run_trading_cycle(self):
        """Run one complete trading cycle"""
        print(f"\n🔄 Trading Cycle - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        signals_generated = 0
        trades_executed = 0
        
        for symbol in self.symbols:
            try:
                # Generate signal
                signal_data = self.generate_trading_signal(symbol)
                
                if signal_data['signal'] != 'HOLD':
                    signals_generated += 1
                    print(f"📊 {symbol}: {signal_data['signal']} "
                          f"(Confidence: {signal_data['confidence']:.1%})")
                    
                    # Execute trade if confidence is high enough
                    if self.execute_trade(symbol, signal_data):
                        trades_executed += 1
                
            except Exception as e:
                print(f"❌ Error processing {symbol}: {e}")
        
        # Show summary
        print(f"\n📈 Cycle Summary:")
        print(f"   Signals Generated: {signals_generated}")
        print(f"   Trades Executed: {trades_executed}")
        print(f"   Daily Trades: {self.daily_trades}")
        
        # Show account status
        if self.mode == 'paper':
            summary = self.paper_account.get_portfolio_summary()
            print(f"   Portfolio Value: ₹{summary['total_portfolio_value']:,.2f}")
            print(f"   Total Return: {summary['total_return_pct']:+.2f}%")
        
        print("=" * 60)
    
    def start_live_trading(self, check_interval_minutes=15):
        """Start live trading system"""
        if not self.initialize_system():
            return
        
        print(f"\n🚀 Starting Live Trading System")
        print(f"Mode: {self.mode.upper()}")
        print(f"Check interval: {check_interval_minutes} minutes")
        print("Press Ctrl+C to stop")
        print("=" * 60)
        
        # Schedule trading cycles
        schedule.every(check_interval_minutes).minutes.do(self.run_trading_cycle)
        
        # Run initial cycle
        self.run_trading_cycle()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute
        except KeyboardInterrupt:
            print("\n🛑 Trading system stopped")
            self.generate_final_report()
    
    def generate_final_report(self):
        """Generate final trading report"""
        print("\n📊 Final Trading Report")
        print("=" * 40)
        
        if self.mode == 'paper':
            summary = self.paper_account.get_portfolio_summary()
            print(f"Initial Balance: ₹{self.paper_account.initial_balance:,.2f}")
            print(f"Final Value: ₹{summary['total_portfolio_value']:,.2f}")
            print(f"Total Return: ₹{summary['total_return']:,.2f} ({summary['total_return_pct']:+.2f}%)")
        
        print(f"Total Trades: {len(self.trade_log)}")
        print(f"Daily Trades: {self.daily_trades}")
        
        if self.trade_log:
            print("\nRecent Trades:")
            for trade in self.trade_log[-5:]:
                print(f"  {trade['timestamp'].strftime('%H:%M')} - "
                      f"{trade['action']} {trade['shares']} {trade['symbol']} "
                      f"@ ₹{trade['price']:.2f}")

def main():
    print("🏦 Live Trading System")
    print("=" * 30)
    
    mode = input("Select mode (paper/live): ").lower()
    if mode not in ['paper', 'live']:
        mode = 'paper'
    
    if mode == 'live':
        broker = input("Select broker (zerodha/upstox): ").lower()
        if broker not in ['zerodha', 'upstox']:
            broker = 'zerodha'
    else:
        broker = 'zerodha'  # Default for paper trading
    
    # Create and start trading system
    trading_system = LiveTradingSystem(broker_type=broker, mode=mode)
    trading_system.start_live_trading(check_interval_minutes=10)

if __name__ == "__main__":
    main()