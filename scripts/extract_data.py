import yfinance as yf
import pandas as pd

def extract_data(ticker, start_date, end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    # Flatten MultiIndex columns from yfinance
    if isinstance(data.columns, pd.MultiIndex):
        data.columns = data.columns.get_level_values(0)
    # yfinance with auto_adjust=True does not return 'Adj Close', only 'Close', 'Open', etc.
    columns = ['Open', 'High', 'Low', 'Close', 'Volume']
    data = data[columns]
    data.dropna(inplace=True)
    return data