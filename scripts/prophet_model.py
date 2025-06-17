import pandas as pd
from prophet import Prophet

def train_prophet_model(data, steps=30):
    df_prophet = data.reset_index() # converts the index to a column
    df_prophet = df_prophet.rename(columns={'Date': 'ds', 'Close': 'y'})#renames the columns to fit Prophet's requirements
    df_prophet = df_prophet[['ds', 'y']]  #Keep only the necessary columns
    model = Prophet(daily_seasonality=True, yearly_seasonality=True, weekly_seasonality=True)
    model.fit(df_prophet)
    future = model.make_future_dataframe(periods=steps)
    forecast = model.predict(future)
    forecast = forecast[['ds', 'yhat', 'yhat_lower', 'yhat_upper']]