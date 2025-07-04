import pandas as pd


def simple_backtest(data, signal_column='Signal'):
    capital = 10000  # Starting capital
    position = 0  # Current position (number of shares)
    portfolio_value = []  # To track portfolio value over time
    for i in range(1, len(data)):
        price = data['Close'].iloc[i]
        signal = data[signal_column].iloc[i]
        if signal == 'Buy' and position == 0: # Initializing a position
            position = capital // price # Buy as many shares as possible
            capital = 0 # Reset capital to zero after buying shares
        elif signal == 'Sell' and position > 0: # Closing a position
            capital += position * price # Sell all shares
            position = 0 # Reset position to zero after selling shares
        elif signal == 'Hold': # Holding the position
            pass
        portfolio_value.append(capital + position * price) # final value of the portfolio
    data = data.iloc[1:].copy()
    data['Portfolio Value'] = portfolio_value
    # Reset index and add a 'Date' column if not present
    if 'Date' not in data.columns:
        data = data.reset_index().rename(columns={'index': 'Date'})
    return data[['Date', 'Close', 'Portfolio Value']]
