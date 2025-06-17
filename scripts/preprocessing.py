import pandas as pd
import numpy as np
def preprocess_data(data):
    data['Log returns'] = np.log(data['Close'] / data['Close'].shift(1)) # calulating the log returns
    data['Volatility'] = data['Log returns'].rolling(window=30).std()  # 30-day rolling volatility
    data['SMA_50'] = data['Close'].rolling(window=50).mean()  # 50-day simple moving average
    return data.dropna()  # drop rows with NaN values after calculations
