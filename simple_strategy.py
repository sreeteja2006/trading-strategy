#!/usr/bin/env python3
"""
Simplified trading strategy without heavy ML dependencies
"""
import sys
import os
sys.path.append('scripts')

# Import required modules
import extract_data
import backtester
import prophet_model
import arima_model
import rf_model
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
from strategy import generate_signals
from preprocessing import preprocess_data

def main():
    print("🚀 Starting Trading Strategy Analysis...")
    print("=" * 50)
    
    # Configuration
    stock_name = "RELIANCE.NS"
    start_date = "2023-01-01"
    end_date = "2024-12-31"
    
    print(f"📊 Analyzing: {stock_name}")
    print(f"📅 Period: {start_date} to {end_date}")
    print()
    
    try:
        # Download and preprocess data
        print("📥 Downloading stock data...")
        stock_data = extract_data.extract_data(stock_name, start_date, end_date)
        stock_data = preprocess_data(stock_data)
        print(f"✅ Downloaded {len(stock_data)} data points")
        
        # Show recent data
        print("\n📈 Recent Stock Data:")
        print(stock_data[['Close', 'Volume', 'RSI_14', 'MACD']].tail())
        
        # Get predictions from models (excluding LSTM)
        print("\n🤖 Running ML Models...")
        
        # Get target dates for prediction
        last_dates = stock_data.index[-7:]
        
        # Prophet model
        print("  - Prophet forecasting...")
        future_prices_prophet, _ = prophet_model.train_prophet_model(stock_data, steps=7)
        forecast_on_real_dates_prophet = future_prices_prophet[future_prices_prophet['ds'].isin(last_dates)]
        
        # ARIMA model
        print("  - ARIMA forecasting...")
        _, future_prices_arima = arima_model.train_arima_model(stock_data, steps=7)
        
        # Random Forest model
        print("  - Random Forest forecasting...")
        predicted_prices_rf = rf_model.train_rf_model(stock_data, steps=7, target_dates=last_dates)
        
        # Create ensemble prediction (without LSTM)
        predicted_prices_prophet = pd.Series(
            forecast_on_real_dates_prophet['yhat'].values,
            index=last_dates,
            dtype=float
        )
        
        predicted_prices_arima = pd.Series(
            future_prices_arima.values,
            index=last_dates,
            dtype=float
        )
        
        # Ensemble prediction (3 models instead of 4)
        ensemble_pred = pd.DataFrame({
            'prophet': predicted_prices_prophet,
            'arima': predicted_prices_arima,
            'rf': predicted_prices_rf
        }).mean(axis=1)
        
        print("✅ All models completed!")
        
        # Show predictions
        print("\n🔮 Price Predictions (Next 7 Days):")
        print("=" * 40)
        actual_prices = stock_data.loc[last_dates, 'Close']
        
        for date, actual, predicted in zip(last_dates, actual_prices, ensemble_pred):
            change = ((predicted - actual) / actual) * 100
            direction = "📈" if change > 0 else "📉"
            print(f"{date.strftime('%Y-%m-%d')}: ₹{actual:.2f} → ₹{predicted:.2f} {direction} ({change:+.1f}%)")
        
        # Generate trading signals
        print("\n📊 Generating Trading Signals...")
        signals = generate_signals(ensemble_pred, actual_prices, threshold=0.02)
        
        # Add signals to stock data
        stock_data = stock_data.copy()
        stock_data['Signal'] = 'Hold'
        if len(signals) == len(last_dates) and len(stock_data) >= len(last_dates):
            stock_data.iloc[-len(last_dates):, stock_data.columns.get_loc('Signal')] = signals
        
        # Show signals
        print("\n🎯 Trading Signals:")
        print("=" * 30)
        signal_data = stock_data[stock_data['Signal'] != 'Hold'].tail(10)
        if not signal_data.empty:
            for date, row in signal_data.iterrows():
                signal_emoji = "🟢" if row['Signal'] == 'Buy' else "🔴"
                print(f"{date.strftime('%Y-%m-%d')}: {signal_emoji} {row['Signal']} at ₹{row['Close']:.2f}")
        else:
            print("No buy/sell signals generated (all Hold)")
        
        # Run backtest
        print("\n💰 Running Backtest...")
        result = backtester.simple_backtest_with_risk(stock_data, signal_column='Signal')
        metrics = backtester.risk_metrics(result)
        
        # Show results
        print("\n📊 Performance Metrics:")
        print("=" * 30)
        for key, value in metrics.items():
            if isinstance(value, float):
                if 'return' in key.lower() or 'ratio' in key.lower():
                    print(f"{key.replace('_', ' ').title()}: {value:.2%}")
                else:
                    print(f"{key.replace('_', ' ').title()}: {value:.4f}")
            else:
                print(f"{key.replace('_', ' ').title()}: {value}")
        
        # Show portfolio performance
        initial_value = result['Portfolio Value'].iloc[0]
        final_value = result['Portfolio Value'].iloc[-1]
        total_return = (final_value - initial_value) / initial_value * 100
        
        print(f"\n💼 Portfolio Performance:")
        print("=" * 30)
        print(f"Initial Value: ₹{initial_value:,.2f}")
        print(f"Final Value: ₹{final_value:,.2f}")
        print(f"Total Return: {total_return:+.2f}%")
        
        # Generate charts
        print("\n📈 Generating Charts...")
        
        # Price chart with signals
        plt.figure(figsize=(12, 8))
        plt.subplot(2, 1, 1)
        plt.plot(stock_data.index, stock_data['Close'], label='Close Price', alpha=0.7)
        
        # Plot buy/sell signals
        buys = stock_data[stock_data['Signal'] == 'Buy']
        sells = stock_data[stock_data['Signal'] == 'Sell']
        
        if not buys.empty:
            plt.scatter(buys.index, buys['Close'], marker='^', color='green', s=100, label='Buy Signal')
        if not sells.empty:
            plt.scatter(sells.index, sells['Close'], marker='v', color='red', s=100, label='Sell Signal')
        
        plt.title(f'{stock_name} - Price and Trading Signals')
        plt.ylabel('Price (₹)')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # Portfolio value chart
        plt.subplot(2, 1, 2)
        plt.plot(result.index, result['Portfolio Value'], color='purple', linewidth=2)
        plt.title('Portfolio Value Over Time')
        plt.ylabel('Portfolio Value (₹)')
        plt.xlabel('Date')
        plt.grid(True, alpha=0.3)
        
        plt.tight_layout()
        plt.savefig('trading_analysis.png', dpi=300, bbox_inches='tight')
        print("✅ Chart saved as 'trading_analysis.png'")
        
        print("\n🎉 Analysis Complete!")
        print("=" * 50)
        
    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()