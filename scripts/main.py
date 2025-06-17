import extract_data
import backtester
import prophet_model
import arima_model
import pandas as pd
import matplotlib.pyplot as plt
from strategy import generate_signals
import argparse
import logging


logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def parse_args():
    parser = argparse.ArgumentParser(description="Forecast stock prices and backtest trading strategy.")
    parser.add_argument("--stock", type=str, default="RELIANCE.NS", help="Stock ticker symbol (e.g., RELIANCE.NS)")
    parser.add_argument("--start", type=str, default="2023-01-01", help="Start date in YYYY-MM-DD format")
    parser.add_argument("--end", type=str, default="2024-12-31", help="End date in YYYY-MM-DD format")
    return parser.parse_args()
def plot_forecast_vs_actual(actual_prices, predicted_prices):
    plt.figure(figsize=(10, 5))
    plt.plot(actual_prices.index, actual_prices, label='Real Price')
    plt.plot(predicted_prices.index, predicted_prices, label='Forecast')
    plt.title('Forecast vs Real Price')
    plt.xlabel('Days')
    plt.ylabel('Price')
    plt.legend()
    plt.grid()
    plt.show()

def plot_buy_sell_signals(stock_data):
    plt.figure(figsize=(10, 5))
    plt.plot(stock_data['Close'], label='Close Price', color='blue')

    buys = stock_data[stock_data['Signal'] == 'Buy']
    sells = stock_data[stock_data['Signal'] == 'Sell']

    plt.scatter(buys.index, buys['Close'], marker='^', color='green', label='Buy')
    plt.scatter(sells.index, sells['Close'], marker='v', color='red', label='Sell')

    plt.title('Buy/Sell Points')
    plt.xlabel('Days')
    plt.ylabel('Price')
    plt.legend()
    plt.grid()
    plt.show()

def plot_portfolio_value(result):
    plt.figure(figsize=(10, 5))
    plt.plot(result['Portfolio Value'], label='Money Over Time', color='purple')
    plt.title('Portfolio Value (Backtest)')
    plt.xlabel('Date')
    plt.ylabel('Money')
    plt.legend()
    plt.grid()
    plt.show()
def forecasted_7days(stock_data, future_prices, steps=7):
    last_date = stock_data.index[-1]
    future_only = future_prices[future_prices['ds'] > last_date].head(steps)
    if not future_only.empty:
        print(f'Future forecasted prices (next {steps} days) with timestamps:')
        print(future_only[['ds', 'yhat', 'yhat_lower', 'yhat_upper']].to_string(index=False))
        plt.figure(figsize=(10, 5))
        plt.plot(future_only['ds'], future_only['yhat'], label='Forecasted Future Price', color='orange')
        plt.fill_between(future_only['ds'], future_only['yhat_lower'], future_only['yhat_upper'], color='orange', alpha=0.2, label='Confidence Interval')
        plt.title(f'Forecasted Future Prices (Next {steps} Days)')
        plt.xlabel('Date & Time')
        plt.ylabel('Forecasted Price')
        plt.xticks(rotation=45)
        plt.legend()
        plt.grid()
        plt.tight_layout()
        plt.show()
    else:
        print('No future forecasted prices available (all forecast dates are within the historical data range).')
def main(stock_name, start, end):
    # Step 1: Pick stock and time period
    stock_name = 'GRANULES.NS'
    start = '2024-06-01'
    end = '2025-06-01'

    # Step 2: Download historical stock prices
    stock_data = extract_data.extract_data(stock_name, start, end)

    # Step 3: Forecast future prices using Prophet model (steps=7 for one week)
    future_prices, model = prophet_model.train_prophet_model(stock_data, steps=7)

    # Step 4: Align forecast and real prices by date
    last_dates = stock_data.index[-30:]
    forecast_on_real_dates = future_prices[future_prices['ds'].isin(last_dates)]
    actual_prices = stock_data.loc[last_dates, 'Close'].reset_index(drop=True)
    predicted_prices = forecast_on_real_dates['yhat'].reset_index(drop=True)

    logging.info('Forecast dates:', forecast_on_real_dates['ds'].tolist())
    logging.info('Actual dates:', last_dates.tolist())

    # Step 5: Generate trading signals
    signals = generate_signals(predicted_prices, actual_prices, threshold=0.02)
    logging.info('Signals generated:', signals)

    # Step 6: Add signals to the last `days` rows of the stock_data
    stock_data = stock_data.copy()
    stock_data['Signal'] = 'Hold'
    if len(signals) == len(last_dates) and len(stock_data) >= len(last_dates):
        stock_data.iloc[-len(last_dates):, stock_data.columns.get_loc('Signal')] = signals
    logging.info('Signal counts after assignment:')
    logging.info(stock_data['Signal'].value_counts())

    # Step 7: Backtest the strategy
    result = backtester.simple_backtest(stock_data, signal_column='Signal')

    # Step 8: Save backtest result to CSV
    result.to_csv('backtest_results.csv', index=False)

    logging.info('Backtest results saved to backtest_results.csv')
    # Step 9: Plot results
    plot_forecast_vs_actual(actual_prices, predicted_prices)
    plot_buy_sell_signals(stock_data)
    plot_portfolio_value(result)
    forecasted_7days(stock_data, future_prices, steps=7)



if __name__ == "__main__":
    args = parse_args()
    main(args.stock, args.start, args.end)
