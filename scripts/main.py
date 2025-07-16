import extract_data
import backtester
import prophet_model
import arima_model
import lstm_model
import rf_model
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Change from 'TkAgg' to 'Agg' for non-interactive backend
import matplotlib.pyplot as plt
from strategy import generate_signals
import argparse
import logging
from preprocessing import preprocess_data

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")


def parse_args():
    parser = argparse.ArgumentParser(description="Forecast stock prices and backtest trading strategy.")
    parser.add_argument("--stock", type=str, default="RELIANCE.NS", help="Stock ticker symbol (e.g., RELIANCE.NS)")
    parser.add_argument("--start", type=str, default="2023-01-01", help="Start date in YYYY-MM-DD format")
    parser.add_argument("--end", type=str, default="2024-12-31", help="End date in YYYY-MM-DD format")
    return parser.parse_args()

def plot_forecast_vs_actual(actual_prices, predicted_prices, arima_prices=None, ensemble_prices=None):
    plt.figure(figsize=(10, 5))
    plt.plot(actual_prices.index, actual_prices, label='Real Price')
    plt.plot(predicted_prices.index, predicted_prices, label='Prophet Forecast')
    if arima_prices is not None:
        plt.plot(arima_prices.index, arima_prices, label='ARIMA Forecast')
    if ensemble_prices is not None:
        plt.plot(ensemble_prices.index, ensemble_prices, label='Ensemble Forecast', linestyle='--')
    plt.title('Forecast vs Real Price')
    plt.xlabel('Days')
    plt.ylabel('Price')
    plt.legend()
    plt.grid()
    plt.savefig('forecast_vs_actual.png')
    plt.close()

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
    plt.savefig('buy_sell_signals.png')
    plt.close()

def plot_portfolio_value(result):
    plt.figure(figsize=(10, 5))
    plt.plot(result['Portfolio Value'], label='Money Over Time', color='purple')
    plt.title('Portfolio Value (Backtest)')
    plt.xlabel('Date')
    plt.ylabel('Money')
    plt.legend()
    plt.grid()
    plt.savefig('portfolio_value.png')
    plt.close()

def plot_technical_indicators(data):
    plt.figure(figsize=(14, 8))
    plt.subplot(3, 1, 1)
    plt.plot(data['Close'], label='Close')
    plt.plot(data['EMA_20'], label='EMA 20')
    plt.plot(data['BB_Upper'], label='BB Upper', linestyle='--', color='grey')
    plt.plot(data['BB_Lower'], label='BB Lower', linestyle='--', color='grey')
    plt.fill_between(data.index, data['BB_Lower'], data['BB_Upper'], color='lightgrey', alpha=0.3)
    plt.title('Price, EMA, Bollinger Bands')
    plt.legend()
    plt.grid()

    plt.subplot(3, 1, 2)
    plt.plot(data['RSI_14'], label='RSI 14', color='purple')
    plt.axhline(70, color='red', linestyle='--')
    plt.axhline(30, color='green', linestyle='--')
    plt.title('RSI')
    plt.legend()
    plt.grid()

    plt.subplot(3, 1, 3)
    plt.plot(data['MACD'], label='MACD', color='blue')
    plt.plot(data['MACD_Signal'], label='MACD Signal', color='orange')
    plt.title('MACD')
    plt.legend()
    plt.grid()

    plt.tight_layout()
    plt.savefig('technical_indicators.png')
    plt.close()

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
        plt.savefig('forecast_7days.png')
        plt.close()
    else:
        print('No future forecasted prices available (all forecast dates are within the historical data range).')

def main(stock_name, start, end):
    # Downloading historical stock prices
    stock_data = extract_data.extract_data(stock_name, start, end)
    stock_data = preprocess_data(stock_data)
    plot_technical_indicators(stock_data)

    # Get target dates for prediction
    last_dates = stock_data.index[-7:]
    
    # Get predictions from each model
    future_prices_prophet, _ = prophet_model.train_prophet_model(stock_data, steps=7)
    forecast_on_real_dates_prophet = future_prices_prophet[future_prices_prophet['ds'].isin(last_dates)]
    
    _, future_prices_arima = arima_model.train_arima_model(stock_data, steps=7)
    
    predicted_prices_lstm = lstm_model.train_lstm_model(stock_data, steps=7)
    predicted_prices_rf = rf_model.train_rf_model(stock_data, steps=7, target_dates=last_dates)
    
    # Convert predictions to numeric Series with datetime index
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
    
    # Ensure all predictions are numeric and aligned
    ensemble_pred = pd.DataFrame({
        'prophet': predicted_prices_prophet,
        'arima': predicted_prices_arima,
        'lstm': predicted_prices_lstm,
        'rf': predicted_prices_rf
    }).mean(axis=1)

    actual_prices = stock_data.loc[last_dates, 'Close'].reset_index(drop=True)

    signals = generate_signals(ensemble_pred, actual_prices, threshold=0.02)
    stock_data = stock_data.copy()
    stock_data['Signal'] = 'Hold'
    if len(signals) == len(last_dates) and len(stock_data) >= len(last_dates):
        stock_data.iloc[-len(last_dates):, stock_data.columns.get_loc('Signal')] = signals

    result = backtester.simple_backtest_with_risk(stock_data, signal_column='Signal')
    metrics = backtester.risk_metrics(result)
    print("Risk Metrics:", metrics)
    plot_portfolio_value(result)
    forecasted_7days(stock_data, future_prices_prophet, steps=7)
    plot_technical_indicators(stock_data)

    # Run backtest with costs
    result, transactions = backtester.simple_backtest_with_costs(
        stock_data, 
        signal_column='Signal',
        commission_pct=0.001,  # 0.1% commission
        slippage_pct=0.001    # 0.1% slippage
    )
    
    # Generate report
    report = Report(stock_data, ensemble_pred, transactions, metrics)
    
    # Save HTML report
    with open('report.html', 'w') as f:
        f.write(report.generate_html())
    
    # Optional: Send notifications
    if os.getenv('TELEGRAM_TOKEN'):
        report.send_telegram(
            os.getenv('TELEGRAM_TOKEN'),
            os.getenv('TELEGRAM_CHAT_ID')
        )

if __name__ == "__main__":
    args = parse_args()
    main(args.stock, args.start, args.end)
