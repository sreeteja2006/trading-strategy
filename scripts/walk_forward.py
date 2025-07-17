import pandas as pd
from sklearn.model_selection import TimeSeriesSplit
from . import prophet_model, arima_model, lstm_model, rf_model

def walk_forward_analysis(data, n_splits=5, train_size=252, test_size=63):
    """
    Perform walk-forward optimization
    train_size: 1 year of trading days
    test_size: 3 months of trading days
    """
    tscv = TimeSeriesSplit(n_splits=n_splits, test_size=test_size)
    results = []
    
    for train_idx, test_idx in tscv.split(data):
        train_data = data.iloc[train_idx]
        test_data = data.iloc[test_idx]
        
        # Train models
        prophet_pred = prophet_model.train_prophet_model(train_data, steps=len(test_idx))
        arima_pred = arima_model.train_arima_model(train_data, steps=len(test_idx))
        lstm_pred = lstm_model.train_lstm_model(train_data, steps=len(test_idx))
        rf_pred = rf_model.train_rf_model(train_data, steps=len(test_idx))
        
        # Combine predictions
        ensemble_pred = pd.DataFrame({
            'prophet': prophet_pred,
            'arima': arima_pred,
            'lstm': lstm_pred,
            'rf': rf_pred
        }).mean(axis=1)
        
        # Calculate metrics
        period_results = {
            'period': f"{train_data.index[-1]} to {test_data.index[-1]}",
            'mse': ((ensemble_pred - test_data['Close'])**2).mean(),
            'sharpe': calculate_sharpe_ratio(ensemble_pred, test_data['Close'])
        }
        results.append(period_results)
    
    return pd.DataFrame(results)