from statsmodels.tsa.arima.model import ARIMA
import pandas as pd
from sklearn.metrics import mean_squared_error
import numpy as np

def train_arima_model(data, order=(5, 1, 0),steps = 30):
    model = ARIMA(data['Close'], order=order)
    model_fit = model.fit()
    forecast = model_fit.forecast(steps=steps)
    mse = mean_squared_error(data['Close'][-steps:], forecast)
    return model_fit, forecast, mse