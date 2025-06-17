import extract_data
import backtester
import prophet_model
import arima_model
import pandas as pd
import matplotlib.pyplot as plt
from strategy import generate_signals

def main():
    # Step 1: Pick stock and time period
    stock_name = 'RELIANCE.NS'
    start = '2023-01-01'
    end = '2024-12-31'

    # Step 2: Download historical stock prices
    stock_data = extract_data.extract_data(stock_name, start, end)
  
    print(stock_data.head())

    # Step 3: Forecast future prices using Prophet model
    future_prices, model = prophet_model.train_prophet(stock_data)
  
    # Step 4: Compare forecast with real prices to create buy/sell signals
    days = 30  # how many days into the future we forecast
    actual_prices = stock_data['Adj Close'][-days:].reset_index(drop=True)
    predicted_prices = future_prices['yhat'][-days:]

    # Step 5: Create buy/sell/hold signals
    signals = generate_signals(predicted_prices, actual_prices, threshold=0.02)
    stock_data = stock_data.copy()
    stock_data['Signal'] = 'Hold'
    stock_data.loc[stock_data.index[-days:], 'Signal'] = signals
    
    print(stock_data.tail(10)[['Adj Close', 'Signal']])

    # Step 6: Backtest – see what would’ve happened if we followed these signals
    result = backtester.simple_backtest(stock_data, signal_column='Signal')
    print("Backtesting done.")
    print(result.tail())

    # Step 7: Save results to a CSV file
    result.to_csv('backtest_results.csv', index=False)


    # Step 8: Plot forecasted vs actual prices
    plt.figure(figsize=(10, 5))
    plt.plot(actual_prices.index, actual_prices, label='Real Price')
    plt.plot(predicted_prices.index, predicted_prices, label='Forecast')
    plt.title('Forecast vs Real Price')
    plt.xlabel('Days')
    plt.ylabel('Price')
    plt.legend()
    plt.grid()
    plt.show()

    # Step 9: Show where we said "Buy" and "Sell"
    plt.figure(figsize=(10, 5))
    plt.plot(stock_data['Adj Close'], label='Price', color='blue')

    buys = stock_data[stock_data['Signal'] == 'Buy']
    sells = stock_data[stock_data['Signal'] == 'Sell']

    plt.scatter(buys.index, buys['Adj Close'], marker='^', color='green', label='Buy')
    plt.scatter(sells.index, sells['Adj Close'], marker='v', color='red', label='Sell')

    plt.title('Buy/Sell Points')
    plt.xlabel('Date')
    plt.ylabel('Price')
    plt.legend()
    plt.grid()
    plt.show()

    # Step 10: Plot how our money would have grown or shrunk
    plt.figure(figsize=(10, 5))
    plt.plot(result['Portfolio Value'], label='Money Over Time', color='purple')
    plt.title('Portfolio Value (Backtest)')
    plt.xlabel('Date')
    plt.ylabel('Money')
    plt.legend()
    plt.grid()
    plt.show()

if __name__ == "__main__":
    main()
