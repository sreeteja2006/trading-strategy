import pandas as pd
from sklearn.ensemble import RandomForestRegressor

def train_rf_model(data, steps=7):
    df = data.copy()
    df['SMA_10'] = df['Close'].rolling(window=10).mean()
    df['SMA_30'] = df['Close'].rolling(window=30).mean()
    df = df.dropna()
    X = df[['SMA_10', 'SMA_30']]
    y = df['Close']
    model = RandomForestRegressor(n_estimators=100)
    model.fit(X, y)
    last_row = X.iloc[-1]
    preds = []
    for _ in range(steps):
        pred = model.predict([last_row])[0]
        preds.append(pred)
        last_row['SMA_10'] = pred
        last_row['SMA_30'] = pred
    forecast_dates = pd.date_range(data.index[-1], periods=steps+1, freq='B')[1:]
    return pd.Series(preds, index=forecast_dates)