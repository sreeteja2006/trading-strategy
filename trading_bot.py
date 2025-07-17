#!/usr/bin/env python3
"""
Automated Trading Bot - Executes trades based on your strategy
"""
import sys
sys.path.append('scripts')

import time
import schedule
from datetime import datetime, timedelta
import yfinance as yf
import pandas as pd
from paper_trading import PaperTradingAccount
import extract_data
import prophet_model
import arima_model
import rf_model
from strategy import generate_signals
from preprocessing import preprocess_data

class TradingBot:
    def __init__(self, symbols=['RELIANCE.NS'], initial_balance=100000):
        self.symbols = symbols
        self.account = PaperTradingAccount(initial_balance)
        self.account.load_account()  # Load existing account if available
        
        # Strategy parameters
        self.signal_threshold = 0.02  # 2%
        self.position_size = 0.1  # 10% of portfolio per position
        self.max_positions = 5
        
        # Performance tracking
        self.daily_returns = []
        self.signals_generated = []
        
    def get_market_data(self, symbol, period="30d"):
        """Get recent market data for analysis"""
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period)
            return data if not data.empty else None
        except Exception as e:
            print(f"Error getting data for {symbol}: {e}")
            return None
    
    def generate_trading_signal(self, symbol):
        """Generate trading signal using your ML strategy"""
        try:
            print(f"🤖 Analyzing {symbol}...")
            
            # Get historical data
            data = self.get_market_data(symbol, period="60d")
            if data is None:
                return None, "No data available"
            
            # Preprocess data
            processed_data = preprocess_data(data)
            
            # Get predictions from models
            last_dates = processed_data.index[-3:]  # Last 3 days for prediction
            
            # Prophet model
            future_prices_prophet, _ = prophet_model.train_prophet_model(processed_data, steps=3)
            forecast_prophet = future_prices_prophet[future_prices_prophet['ds'].isin(last_dates)]
            
            # ARIMA model
            _, future_prices_arima = arima_model.train_arima_model(processed_data, steps=3)
            
            # Random Forest model
            predicted_prices_rf = rf_model.train_rf_model(processed_data, steps=3, target_dates=last_dates)
            
            # Create ensemble prediction
            if not forecast_prophet.empty and len(future_prices_arima) > 0:
                predicted_prices_prophet = pd.Series(
                    forecast_prophet['yhat'].values[:len(last_dates)],
                    index=last_dates,
                    dtype=float
                )
                
                predicted_prices_arima = pd.Series(
                    future_prices_arima[:len(last_dates)],
                    index=last_dates,
                    dtype=float
                )
                
                # Ensemble prediction
                ensemble_pred = pd.DataFrame({
                    'prophet': predicted_prices_prophet,
                    'arima': predicted_prices_arima,
                    'rf': predicted_prices_rf[:len(last_dates)]
                }).mean(axis=1)
                
                # Get actual prices for signal generation
                actual_prices = processed_data.loc[last_dates, 'Close']
                
                # Generate signals
                signals = generate_signals(ensemble_pred, actual_prices, threshold=self.signal_threshold)
                
                # Get the most recent signal
                if len(signals) > 0:
                    latest_signal = signals[-1]
                    current_price = actual_prices.iloc[-1]
                    predicted_price = ensemble_pred.iloc[-1]
                    
                    confidence = abs((predicted_price - current_price) / current_price)
                    
                    return {
                        'signal': latest_signal,
                        'current_price': current_price,
                        'predicted_price': predicted_price,
                        'confidence': confidence,
                        'timestamp': datetime.now()
                    }, "Success"
                
            return None, "Could not generate reliable signal"
            
        except Exception as e:
            return None, f"Error generating signal: {str(e)}"
    
    def calculate_position_size(self, symbol, signal_data):
        """Calculate how many shares to buy/sell"""
        portfolio_value = self.account.get_portfolio_value()
        max_investment = portfolio_value * self.position_size
        
        shares = int(max_investment / signal_data['current_price'])
        return max(1, shares)  # At least 1 share
    
    def execute_trade(self, symbol, signal_data):
        """Execute buy/sell trade"""
        try:
            signal = signal_data['signal']
            current_price = signal_data['current_price']
            
            if signal == 'Buy':
                # Check if we already have a position
                if symbol in self.account.positions:
                    return False, f"Already have position in {symbol}"
                
                # Check if we have too many positions
                if len(self.account.positions) >= self.max_positions:
                    return False, "Maximum positions reached"
                
                shares = self.calculate_position_size(symbol, signal_data)
                success, message = self.account.buy_stock(symbol, shares, current_price)
                
                if success:
                    self.log_trade(symbol, 'BUY', shares, current_price, signal_data)
                
                return success, message
                
            elif signal == 'Sell':
                # Check if we have a position to sell
                if symbol not in self.account.positions:
                    return False, f"No position in {symbol} to sell"
                
                shares = self.account.positions[symbol]['shares']
                success, message = self.account.sell_stock(symbol, shares, current_price)
                
                if success:
                    self.log_trade(symbol, 'SELL', shares, current_price, signal_data)
                
                return success, message
            
            return False, "No actionable signal"
            
        except Exception as e:
            return False, f"Error executing trade: {str(e)}"
    
    def log_trade(self, symbol, action, shares, price, signal_data):
        """Log trade details"""
        log_entry = {
            'timestamp': datetime.now(),
            'symbol': symbol,
            'action': action,
            'shares': shares,
            'price': price,
            'confidence': signal_data['confidence'],
            'predicted_price': signal_data['predicted_price']
        }
        
        self.signals_generated.append(log_entry)
        
        print(f"🎯 TRADE EXECUTED: {action} {shares} {symbol} @ ₹{price:.2f}")
        print(f"   Confidence: {signal_data['confidence']:.1%}")
        print(f"   Predicted: ₹{signal_data['predicted_price']:.2f}")
    
    def run_trading_cycle(self):
        """Run one complete trading cycle"""
        print(f"\n🚀 Trading Cycle Started - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print("=" * 60)
        
        # Check each symbol
        for symbol in self.symbols:
            try:
                # Generate signal
                signal_data, status = self.generate_trading_signal(symbol)
                
                if signal_data is None:
                    print(f"⚠️  {symbol}: {status}")
                    continue
                
                print(f"📊 {symbol}: {signal_data['signal']} signal "
                      f"(Confidence: {signal_data['confidence']:.1%})")
                
                # Execute trade if signal is strong enough
                if signal_data['confidence'] > 0.01:  # 1% minimum confidence
                    success, message = self.execute_trade(symbol, signal_data)
                    if not success:
                        print(f"   ❌ Trade failed: {message}")
                else:
                    print(f"   ⏸️  Signal too weak, skipping trade")
                    
            except Exception as e:
                print(f"❌ Error processing {symbol}: {e}")
        
        # Show portfolio summary
        self.show_portfolio_summary()
        
        # Save account state
        self.account.save_account()
        print("💾 Account saved")
    
    def show_portfolio_summary(self):
        """Display current portfolio status"""
        summary = self.account.get_portfolio_summary()
        
        print(f"\n💼 Portfolio Summary:")
        print(f"   Cash: ₹{summary['cash_balance']:,.2f}")
        print(f"   Total Value: ₹{summary['total_portfolio_value']:,.2f}")
        print(f"   Total Return: ₹{summary['total_return']:,.2f} ({summary['total_return_pct']:+.2f}%)")
        
        if summary['positions']:
            print(f"   Active Positions: {len(summary['positions'])}")
            for symbol, pos in summary['positions'].items():
                print(f"     {symbol}: {pos['shares']} shares, P&L: ₹{pos['pnl']:+,.2f}")
    
    def start_automated_trading(self, check_interval_minutes=30):
        """Start automated trading with scheduled checks"""
        print(f"🤖 Starting Automated Trading Bot")
        print(f"📊 Monitoring: {', '.join(self.symbols)}")
        print(f"⏰ Check interval: {check_interval_minutes} minutes")
        print(f"💰 Initial balance: ₹{self.account.initial_balance:,.2f}")
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
            print("\n🛑 Trading bot stopped")
            self.show_final_report()
    
    def show_final_report(self):
        """Show final performance report"""
        print("\n📊 Final Performance Report")
        print("=" * 40)
        
        summary = self.account.get_portfolio_summary()
        print(f"Initial Balance: ₹{self.account.initial_balance:,.2f}")
        print(f"Final Value: ₹{summary['total_portfolio_value']:,.2f}")
        print(f"Total Return: ₹{summary['total_return']:,.2f} ({summary['total_return_pct']:+.2f}%)")
        print(f"Total Trades: {len(self.account.transactions)}")
        
        if self.signals_generated:
            print(f"Signals Generated: {len(self.signals_generated)}")

def main():
    # Create trading bot
    bot = TradingBot(
        symbols=['RELIANCE.NS', 'TCS.NS', 'INFY.NS'],
        initial_balance=100000
    )
    
    # Start automated trading
    bot.start_automated_trading(check_interval_minutes=15)  # Check every 15 minutes

if __name__ == "__main__":
    main()