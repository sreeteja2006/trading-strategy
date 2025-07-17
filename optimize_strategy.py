#!/usr/bin/env python3
"""
Strategy optimization and parameter tuning
"""
import sys
sys.path.append('scripts')

import pandas as pd
import numpy as np
from simple_strategy import *
import itertools

def optimize_parameters():
    """Test different parameter combinations to find optimal settings"""
    print("🔧 Optimizing Trading Strategy Parameters...")
    print("=" * 50)
    
    # Parameter ranges to test
    thresholds = [0.01, 0.015, 0.02, 0.025, 0.03]  # 1% to 3%
    rsi_oversold = [20, 25, 30]
    rsi_overbought = [70, 75, 80]
    
    best_return = -float('inf')
    best_params = {}
    results = []
    
    print("Testing parameter combinations...")
    
    for threshold, rsi_low, rsi_high in itertools.product(thresholds, rsi_oversold, rsi_overbought):
        try:
            # Run strategy with these parameters
            result = test_strategy_params(threshold, rsi_low, rsi_high)
            results.append({
                'threshold': threshold,
                'rsi_oversold': rsi_low,
                'rsi_overbought': rsi_high,
                'total_return': result['total_return'],
                'sharpe_ratio': result['sharpe_ratio'],
                'max_drawdown': result['max_drawdown'],
                'num_trades': result['num_trades']
            })
            
            if result['total_return'] > best_return:
                best_return = result['total_return']
                best_params = {
                    'threshold': threshold,
                    'rsi_oversold': rsi_low,
                    'rsi_overbought': rsi_high
                }
                
        except Exception as e:
            continue
    
    # Display results
    results_df = pd.DataFrame(results)
    print("\n📊 Top 5 Parameter Combinations:")
    print("=" * 50)
    top_results = results_df.nlargest(5, 'total_return')
    print(top_results.to_string(index=False))
    
    print(f"\n🏆 Best Parameters:")
    print(f"Threshold: {best_params['threshold']:.1%}")
    print(f"RSI Oversold: {best_params['rsi_oversold']}")
    print(f"RSI Overbought: {best_params['rsi_overbought']}")
    print(f"Best Return: {best_return:.2%}")
    
    return best_params

def test_strategy_params(threshold, rsi_oversold, rsi_overbought):
    """Test strategy with specific parameters"""
    # This is a simplified version - you'd implement the full backtesting logic here
    # For now, return mock results
    return {
        'total_return': np.random.uniform(-0.1, 0.3),  # -10% to +30%
        'sharpe_ratio': np.random.uniform(0, 2),
        'max_drawdown': np.random.uniform(0, 0.2),
        'num_trades': np.random.randint(5, 50)
    }

if __name__ == "__main__":
    optimize_parameters()