import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor

def train_rf_model(data, steps=7, target_dates=None):
    # Prepare features
    df = data.copy()
    df['SMA_10'] = df['Close'].rolling(window=10).mean()
    df['SMA_30'] = df['Close'].rolling(window=30).mean()
    df = df.dropna()
    
    # Train model
    feature_names = ['SMA_10', 'SMA_30']
    X = df[feature_names]
    y = df['Close']
    model = RandomForestRegressor(n_estimators=100, random_state=42)
    model.fit(X, y)
    
    # Use target dates if provided, otherwise generate them
    if target_dates is None:
        last_date = data.index[-1]
        future_dates = pd.date_range(start=last_date, periods=steps+1, freq='B')[1:]
    else:
        future_dates = target_dates
    
    # Generate predictions
    preds = []
    current_features = pd.DataFrame(columns=feature_names)
    current_features.loc[0] = [df['SMA_10'].iloc[-1], df['SMA_30'].iloc[-1]]
    
    for _ in range(len(future_dates)):
        pred = model.predict(current_features)[0]
        preds.append(pred)
        # Update features for next prediction
        current_features['SMA_10'] = current_features['SMA_30'] = pred
    
    return pd.Series(preds, index=future_dates)