import pandas as pd
import numpy as np

def preprocess_data(data):
    data['Log returns'] = np.log(data['Close'] / data['Close'].shift(1)) # calulating the log returns
    data['Volatility'] = data['Log returns'].rolling(window=30).std()  # 30-day rolling volatility
    data['SMA_50'] = data['Close'].rolling(window=50).mean()  # 50-day simple moving average
    # EMA
    data['EMA_20'] = data['Close'].ewm(span=20, adjust=False).mean()
    # Bollinger Bands
    data['BB_Middle'] = data['Close'].rolling(window=20).mean()
    data['BB_Std'] = data['Close'].rolling(window=20).std()
    data['BB_Upper'] = data['BB_Middle'] + 2 * data['BB_Std']
    data['BB_Lower'] = data['BB_Middle'] - 2 * data['BB_Std']
    # RSI
    delta = data['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    data['RSI_14'] = 100 - (100 / (1 + rs))
    # MACD
    ema12 = data['Close'].ewm(span=12, adjust=False).mean()
    ema26 = data['Close'].ewm(span=26, adjust=False).mean()
    data['MACD'] = ema12 - ema26
    data['MACD_Signal'] = data['MACD'].ewm(span=9, adjust=False).mean()
    return data.dropna()
