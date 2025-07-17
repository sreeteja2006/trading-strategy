import numpy as np
import pandas as pd
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

import tensorflow as tf
tf.config.set_visible_devices([], 'GPU')

from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense
from sklearn.preprocessing import MinMaxScaler

def train_lstm_model(data, steps=7):
    # Prepare data
    close_prices = data['Close'].values.reshape(-1, 1)
    scaler = MinMaxScaler()
    scaled = scaler.fit_transform(close_prices)
    X, y = [], []
    seq_len = 30
    for i in range(len(scaled) - seq_len):
        X.append(scaled[i:i+seq_len])
        y.append(scaled[i+seq_len])
    X, y = np.array(X), np.array(y)
    
    # Build and train model
    model = Sequential([
        LSTM(50, input_shape=(seq_len, 1)),
        Dense(1)
    ])
    model.compile(optimizer='adam', loss='mse')
    model.fit(X, y, epochs=10, batch_size=16, verbose=0)
    
    # Get the dates from input data
    last_dates = data.index[-steps:]
    
    # Generate predictions
    last_seq = scaled[-seq_len:].reshape(1, seq_len, 1)
    preds = []
    current_seq = last_seq.copy()
    
    for _ in range(steps):
        pred = model.predict(current_seq, verbose=0)[0][0]
        preds.append(pred)
        current_seq = np.roll(current_seq, -1, axis=1)
        current_seq[0, -1, 0] = pred
    
    # Scale back predictions and create Series with matching dates
    preds = scaler.inverse_transform(np.array(preds).reshape(-1, 1)).flatten()
    return pd.Series(preds, index=last_dates)