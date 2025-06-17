import yfinance as yf
def extract_data(ticker,start_date,end_date):
    data = yf.download(ticker, start=start_date, end=end_date)
    data = data[['Open', 'High', 'Low', 'Close', 'Volume']]
    data.dropna(inplace=True)
    return data