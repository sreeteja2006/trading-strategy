import pandas as pd
from prophet import Prophet

def train_prophet_model(data, steps=30):
    df_prophet = data.reset_index() # converts the index to a column
    # Ensure the date column is named 'ds' and is a Series
    if 'Date' in df_prophet.columns:
        df_prophet = df_prophet.rename(columns={'Date': 'ds', 'Close': 'y'})
    elif 'index' in df_prophet.columns:
        df_prophet = df_prophet.rename(columns={'index': 'ds', 'Close': 'y'})
    else:
        raise ValueError("No date column found in data for Prophet.")
    df_prophet = df_prophet[['ds', 'y']]
    df_prophet['ds'] = pd.to_datetime(df_prophet['ds'])
    df_prophet['y'] = pd.to_numeric(df_prophet['y'], errors='coerce')
    model = Prophet(daily_seasonality=True, yearly_seasonality=True, weekly_seasonality=True)
    model.fit(df_prophet)
    future = model.make_future_dataframe(periods=steps)
    forecast = model.predict(future)
    forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]
    return forecast