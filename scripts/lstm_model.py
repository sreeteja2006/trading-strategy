import numpy as np
import pandas as pd
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler

def train_lstm_model(data, steps=7):
    close_prices = data['Close'].values.reshape(-1, 1)
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(close_prices)
    X, y = [], []
    seq_len = 30
    for i in range(len(scaled) - seq_len):
        X.append(scaled[i:i+seq_len])
        y.append(scaled[i+seq_len])
    X, y = np.array(X), np.array(y)
    model = Sequential([
        LSTM(50, input_shape=(seq_len, 1)),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=10, batch_size=16, verbose=0)
    last_seq = scaled[-seq_len:].reshape(1, seq_len, 1)
    preds = []
    for _ in range(steps):
        pred = model.predict(last_seq)[0][0]
        preds.append(pred)
        last_seq = np.roll(last_seq, -1)
        last_seq[0, -1, 0] = pred
    preds = scaler.inverse_transform(np.array(preds).reshape(-1, 1)).flatten()
    forecast_dates = pd.date_range(data.index[-1], periods=steps+1, freq='B')[1:]
    return pd.Series(preds, index=forecast_dates)