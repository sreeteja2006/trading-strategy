import extract_data
import backtester
import prophet_model
import arima_model
import pandas as pd
import yfinance as yf

def main():
    ticker = 'RELIANCE.NS'
    start_date = '2025-01-01'
    end_date = '2025-12-31'
    data = extract_data.extract_data(ticker, start_date, end_date)
    print("Data extracted successfully.")
    print(data.head())
    # Train Prophet model
    prophet_forecast = prophet_model.train_prophet_model(data, steps=30)
    print("Prophet model trained successfully.")
    print(prophet_forecast.head())
    # Train ARIMA model
    arima_model_fit, arima_forecast = arima_model.train_arima_model(data = data, order=(5, 1, 0), steps=30)
    print("ARIMA model trained successfully.") 
    print(arima_forecast.head())
    # Backtest strategy
    backtest_results = backtester.backtest_strategy(data, signal_column='Signal')
    print("Backtest completed successfully.")
    print(backtest_results.head())
    # Save results to CSV
    backtest_results.to_csv('backtest_results.csv', index=False)
    print("Results saved to backtest_results.csv")

if __name__ == "__main__":
    main()
    print("Main function executed successfully.")

