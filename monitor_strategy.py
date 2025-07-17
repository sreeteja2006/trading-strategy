#!/usr/bin/env python3
"""
Real-time strategy monitoring and alerts
"""
import sys
sys.path.append('scripts')

import time
import schedule
from datetime import datetime
import yfinance as yf
import pandas as pd

class TradingMonitor:
    def __init__(self, symbols=['RELIANCE.NS'], check_interval=15):
        self.symbols = symbols
        self.check_interval = check_interval  # minutes
        self.last_prices = {}
        
    def check_signals(self):
        """Check for trading signals in real-time"""
        print(f"🔍 Checking signals at {datetime.now().strftime('%H:%M:%S')}")
        
        for symbol in self.symbols:
            try:
                # Get latest data
                ticker = yf.Ticker(symbol)
                data = ticker.history(period="5d", interval="1m")
                
                if data.empty:
                    continue
                    
                current_price = data['Close'].iloc[-1]
                prev_price = self.last_prices.get(symbol, current_price)
                
                # Calculate price change
                price_change = (current_price - prev_price) / prev_price * 100
                
                # Simple signal logic
                if abs(price_change) > 1.0:  # 1% change threshold
                    direction = "📈 UP" if price_change > 0 else "📉 DOWN"
                    self.send_alert(symbol, current_price, price_change, direction)
                
                self.last_prices[symbol] = current_price
                
            except Exception as e:
                print(f"Error checking {symbol}: {e}")
    
    def send_alert(self, symbol, price, change, direction):
        """Send trading alert"""
        alert_msg = f"""
🚨 TRADING ALERT 🚨
Symbol: {symbol}
Price: ₹{price:.2f}
Change: {change:+.2f}% {direction}
Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
        """
        print(alert_msg)
        
        # Here you could add:
        # - Email notifications
        # - Telegram/WhatsApp alerts
        # - SMS notifications
        # - Discord/Slack webhooks
    
    def start_monitoring(self):
        """Start real-time monitoring"""
        print(f"🚀 Starting real-time monitoring for {self.symbols}")
        print(f"⏰ Checking every {self.check_interval} minutes")
        print("Press Ctrl+C to stop")
        
        # Schedule checks
        schedule.every(self.check_interval).minutes.do(self.check_signals)
        
        # Initial check
        self.check_signals()
        
        try:
            while True:
                schedule.run_pending()
                time.sleep(60)  # Check every minute for scheduled tasks
        except KeyboardInterrupt:
            print("\n🛑 Monitoring stopped")

def main():
    monitor = TradingMonitor(['RELIANCE.NS', 'TCS.NS', 'INFY.NS'])
    monitor.start_monitoring()

if __name__ == "__main__":
    main()