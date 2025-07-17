#!/usr/bin/env python3
"""
Advanced Risk Management System
"""
import sys
sys.path.append('scripts')

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
from typing import Dict, List, Tuple

class RiskManager:
    """Advanced risk management for trading strategies"""
    
    def __init__(self, initial_capital: float = 100000):
        self.initial_capital = initial_capital
        self.current_capital = initial_capital
        
        # Risk parameters
        self.max_portfolio_risk = 0.02  # 2% max portfolio risk per day
        self.max_position_risk = 0.01   # 1% max risk per position
        self.max_sector_exposure = 0.3  # 30% max exposure to any sector
        self.max_single_stock = 0.1     # 10% max in single stock
        
        # Stop loss and take profit
        self.default_stop_loss = 0.05   # 5% stop loss
        self.default_take_profit = 0.15 # 15% take profit
        self.trailing_stop = 0.03       # 3% trailing stop
        
        # Position tracking
        self.positions = {}
        self.sector_exposure = {}
        self.daily_pnl = []
        self.risk_metrics = {}
        
        # Load historical data
        self.load_risk_data()
    
    def load_risk_data(self):
        """Load historical risk data"""
        risk_file = 'risk_data.json'
        if os.path.exists(risk_file):
            with open(risk_file, 'r') as f:
                data = json.load(f)
                self.daily_pnl = data.get('daily_pnl', [])
                self.sector_exposure = data.get('sector_exposure', {})
                self.risk_metrics = data.get('risk_metrics', {})
    
    def save_risk_data(self):
        """Save risk data to file"""
        data = {
            'daily_pnl': self.daily_pnl,
            'sector_exposure': self.sector_exposure,
            'risk_metrics': self.risk_metrics,
            'last_updated': datetime.now().isoformat()
        }
        
        with open('risk_data.json', 'w') as f:
            json.dump(data, f, indent=2)
    
    def calculate_position_size(self, symbol: str, entry_price: float, 
                              stop_loss_price: float) -> int:
        """Calculate optimal position size based on risk"""
        # Risk per share
        risk_per_share = abs(entry_price - stop_loss_price)
        
        # Maximum risk amount
        max_risk_amount = self.current_capital * self.max_position_risk
        
        # Calculate shares
        max_shares = int(max_risk_amount / risk_per_share)
        
        # Check portfolio concentration limits
        max_portfolio_value = self.current_capital * self.max_single_stock
        max_shares_by_concentration = int(max_portfolio_value / entry_price)
        
        # Return the smaller of the two limits
        return min(max_shares, max_shares_by_concentration)
    
    def validate_trade(self, symbol: str, action: str, quantity: int, 
                      price: float, sector: str = None) -> Tuple[bool, str]:
        """Validate if trade meets risk criteria"""
        
        # Check if market is open (basic check)
        now = datetime.now()
        if now.weekday() >= 5:  # Weekend
            return False, "Market is closed (weekend)"
        
        # Check trading hours (9:15 AM to 3:30 PM IST)
        if not (9 <= now.hour < 15 or (now.hour == 15 and now.minute <= 30)):
            return False, "Market is closed (outside trading hours)"
        
        trade_value = quantity * price
        
        if action.upper() == 'BUY':
            # Check available capital
            if trade_value > self.current_capital * 0.9:  # Keep 10% cash
                return False, f"Insufficient capital. Need ₹{trade_value:,.2f}, available ₹{self.current_capital * 0.9:,.2f}"
            
            # Check single stock concentration
            current_exposure = self.positions.get(symbol, {}).get('market_value', 0)
            new_exposure = (current_exposure + trade_value) / self.current_capital
            
            if new_exposure > self.max_single_stock:
                return False, f"Single stock limit exceeded. Max {self.max_single_stock:.1%}, would be {new_exposure:.1%}"
            
            # Check sector concentration
            if sector:
                current_sector_exposure = self.sector_exposure.get(sector, 0)
                new_sector_exposure = (current_sector_exposure + trade_value) / self.current_capital
                
                if new_sector_exposure > self.max_sector_exposure:
                    return False, f"Sector exposure limit exceeded. Max {self.max_sector_exposure:.1%}, would be {new_sector_exposure:.1%}"
        
        elif action.upper() == 'SELL':
            # Check if we have enough shares to sell
            current_quantity = self.positions.get(symbol, {}).get('quantity', 0)
            if quantity > current_quantity:
                return False, f"Insufficient shares. Have {current_quantity}, trying to sell {quantity}"
        
        return True, "Trade validated"
    
    def update_position(self, symbol: str, action: str, quantity: int, 
                       price: float, sector: str = None):
        """Update position tracking"""
        
        if symbol not in self.positions:
            self.positions[symbol] = {
                'quantity': 0,
                'avg_price': 0,
                'market_value': 0,
                'unrealized_pnl': 0,
                'sector': sector
            }
        
        position = self.positions[symbol]
        
        if action.upper() == 'BUY':
            # Update average price
            total_cost = (position['quantity'] * position['avg_price']) + (quantity * price)
            total_quantity = position['quantity'] + quantity
            
            position['avg_price'] = total_cost / total_quantity if total_quantity > 0 else 0
            position['quantity'] = total_quantity
            position['market_value'] = total_quantity * price
            
            # Update sector exposure
            if sector:
                self.sector_exposure[sector] = self.sector_exposure.get(sector, 0) + (quantity * price)
        
        elif action.upper() == 'SELL':
            position['quantity'] -= quantity
            position['market_value'] = position['quantity'] * price
            
            # Update sector exposure
            if sector:
                self.sector_exposure[sector] = max(0, self.sector_exposure.get(sector, 0) - (quantity * price))
            
            # Remove position if quantity is 0
            if position['quantity'] <= 0:
                if sector and sector in self.sector_exposure:
                    self.sector_exposure[sector] = max(0, self.sector_exposure[sector] - position['market_value'])
                del self.positions[symbol]
    
    def calculate_stop_loss(self, symbol: str, entry_price: float, 
                           action: str = 'BUY') -> float:
        """Calculate stop loss price"""
        if action.upper() == 'BUY':
            return entry_price * (1 - self.default_stop_loss)
        else:  # SELL
            return entry_price * (1 + self.default_stop_loss)
    
    def calculate_take_profit(self, symbol: str, entry_price: float, 
                             action: str = 'BUY') -> float:
        """Calculate take profit price"""
        if action.upper() == 'BUY':
            return entry_price * (1 + self.default_take_profit)
        else:  # SELL
            return entry_price * (1 - self.default_take_profit)
    
    def check_stop_loss_take_profit(self, current_prices: Dict[str, float]) -> List[Dict]:
        """Check if any positions hit stop loss or take profit"""
        alerts = []
        
        for symbol, position in self.positions.items():
            if symbol not in current_prices:
                continue
            
            current_price = current_prices[symbol]
            entry_price = position['avg_price']
            
            # Calculate P&L percentage
            pnl_pct = (current_price - entry_price) / entry_price
            
            # Check stop loss
            if pnl_pct <= -self.default_stop_loss:
                alerts.append({
                    'type': 'STOP_LOSS',
                    'symbol': symbol,
                    'current_price': current_price,
                    'entry_price': entry_price,
                    'pnl_pct': pnl_pct,
                    'action': 'SELL',
                    'quantity': position['quantity']
                })
            
            # Check take profit
            elif pnl_pct >= self.default_take_profit:
                alerts.append({
                    'type': 'TAKE_PROFIT',
                    'symbol': symbol,
                    'current_price': current_price,
                    'entry_price': entry_price,
                    'pnl_pct': pnl_pct,
                    'action': 'SELL',
                    'quantity': position['quantity']
                })
        
        return alerts
    
    def calculate_portfolio_metrics(self) -> Dict:
        """Calculate portfolio risk metrics"""
        if not self.daily_pnl:
            return {}
        
        returns = np.array(self.daily_pnl)
        
        # Basic metrics
        total_return = sum(returns)
        avg_return = np.mean(returns)
        volatility = np.std(returns)
        
        # Sharpe ratio (assuming 6% risk-free rate)
        risk_free_rate = 0.06 / 252  # Daily risk-free rate
        sharpe_ratio = (avg_return - risk_free_rate) / volatility if volatility > 0 else 0
        
        # Maximum drawdown
        cumulative_returns = np.cumsum(returns)
        running_max = np.maximum.accumulate(cumulative_returns)
        drawdown = cumulative_returns - running_max
        max_drawdown = np.min(drawdown)
        
        # Win rate
        winning_days = len([r for r in returns if r > 0])
        win_rate = winning_days / len(returns) if returns.size > 0 else 0
        
        # Value at Risk (95% confidence)
        var_95 = np.percentile(returns, 5) if len(returns) > 0 else 0
        
        return {
            'total_return': total_return,
            'avg_daily_return': avg_return,
            'volatility': volatility,
            'sharpe_ratio': sharpe_ratio,
            'max_drawdown': max_drawdown,
            'win_rate': win_rate,
            'var_95': var_95,
            'total_trades': len(returns)
        }
    
    def generate_risk_report(self) -> str:
        """Generate comprehensive risk report"""
        metrics = self.calculate_portfolio_metrics()
        
        report = f"""
🛡️  RISK MANAGEMENT REPORT
{'='*50}

💼 Portfolio Overview:
   Initial Capital: ₹{self.initial_capital:,.2f}
   Current Capital: ₹{self.current_capital:,.2f}
   Active Positions: {len(self.positions)}

📊 Risk Metrics:
   Total Return: ₹{metrics.get('total_return', 0):,.2f}
   Avg Daily Return: {metrics.get('avg_daily_return', 0):.4f}
   Volatility: {metrics.get('volatility', 0):.4f}
   Sharpe Ratio: {metrics.get('sharpe_ratio', 0):.2f}
   Max Drawdown: {metrics.get('max_drawdown', 0):.4f}
   Win Rate: {metrics.get('win_rate', 0):.1%}
   VaR (95%): {metrics.get('var_95', 0):.4f}

🎯 Current Positions:
        """
        
        if self.positions:
            for symbol, pos in self.positions.items():
                pnl = pos['market_value'] - (pos['quantity'] * pos['avg_price'])
                pnl_pct = (pnl / (pos['quantity'] * pos['avg_price'])) * 100 if pos['quantity'] > 0 else 0
                
                report += f"""
   {symbol}: {pos['quantity']} shares @ ₹{pos['avg_price']:.2f}
   Market Value: ₹{pos['market_value']:,.2f}
   P&L: ₹{pnl:+,.2f} ({pnl_pct:+.1f}%)
                """
        else:
            report += "\n   No active positions"
        
        report += f"""

🏭 Sector Exposure:
        """
        
        if self.sector_exposure:
            for sector, exposure in self.sector_exposure.items():
                exposure_pct = (exposure / self.current_capital) * 100
                report += f"\n   {sector}: ₹{exposure:,.2f} ({exposure_pct:.1f}%)"
        else:
            report += "\n   No sector exposure data"
        
        return report
    
    def add_daily_pnl(self, pnl: float):
        """Add daily P&L for tracking"""
        self.daily_pnl.append(pnl)
        
        # Keep only last 252 days (1 year)
        if len(self.daily_pnl) > 252:
            self.daily_pnl = self.daily_pnl[-252:]
        
        self.save_risk_data()

def main():
    """Demo of risk management system"""
    print("🛡️  Risk Management System Demo")
    print("=" * 40)
    
    # Create risk manager
    risk_manager = RiskManager(initial_capital=100000)
    
    # Demo trades
    trades = [
        ('RELIANCE', 'BUY', 10, 1480.40, 'Energy'),
        ('TCS', 'BUY', 5, 3229.70, 'IT'),
        ('INFY', 'BUY', 8, 1592.00, 'IT'),
    ]
    
    for symbol, action, quantity, price, sector in trades:
        # Validate trade
        is_valid, message = risk_manager.validate_trade(symbol, action, quantity, price, sector)
        
        if is_valid:
            print(f"✅ {action} {quantity} {symbol} @ ₹{price:.2f} - {message}")
            risk_manager.update_position(symbol, action, quantity, price, sector)
        else:
            print(f"❌ {action} {quantity} {symbol} @ ₹{price:.2f} - {message}")
    
    # Generate risk report
    print(risk_manager.generate_risk_report())
    
    # Demo stop loss/take profit check
    current_prices = {
        'RELIANCE': 1550.00,  # +4.7% gain
        'TCS': 3100.00,       # -4.0% loss
        'INFY': 1750.00       # +9.9% gain
    }
    
    alerts = risk_manager.check_stop_loss_take_profit(current_prices)
    
    if alerts:
        print("\n🚨 TRADING ALERTS:")
        for alert in alerts:
            print(f"   {alert['type']}: {alert['action']} {alert['quantity']} {alert['symbol']} "
                  f"@ ₹{alert['current_price']:.2f} (P&L: {alert['pnl_pct']:+.1f}%)")

if __name__ == "__main__":
    main()