import pandas as pd


def multi_asset_backtest(stock_data_dict, signal_column='Signal', initial_capital=100000):
    portfolio = {'cash': initial_capital, 'positions': {k: 0 for k in stock_data_dict}}
    history = []
    dates = stock_data_dict[list(stock_data_dict.keys())[0]].index
    for date in dates:
        daily_value = portfolio['cash']
        for ticker, data in stock_data_dict.items():
            price = data.loc[date, 'Close']
            signal = data.loc[date, signal_column]
            if signal == 'Buy' and portfolio['cash'] >= price:
                shares = int(portfolio['cash'] // price)
                portfolio['positions'][ticker] += shares
                portfolio['cash'] -= shares * price
            elif signal == 'Sell' and portfolio['positions'][ticker] > 0:
                portfolio['cash'] += portfolio['positions'][ticker] * price
                portfolio['positions'][ticker] = 0
            daily_value += portfolio['positions'][ticker] * price
        history.append({'Date': date, 'Portfolio Value': daily_value})
    return pd.DataFrame(history)


def position_size(capital, risk_per_trade, stop_loss_pct, price):
    risk_amount = capital * risk_per_trade
    stop_loss_amount = price * stop_loss_pct
    shares = int(risk_amount // stop_loss_amount)
    return shares


def simple_backtest_with_risk(data, signal_column='Signal', initial_capital=100000, risk_per_trade=0.01, stop_loss_pct=0.05, take_profit_pct=0.10):
    capital = initial_capital
    position = 0
    entry_price = 0
    history = []
    for idx, row in data.iterrows():
        price = row['Close']
        signal = row[signal_column]
        if signal == 'Buy' and position == 0:
            shares = position_size(capital, risk_per_trade, stop_loss_pct, price)
            position = shares
            entry_price = price
            capital -= shares * price
        elif signal == 'Sell' and position > 0:
            capital += position * price
            position = 0
            entry_price = 0
        # Stop-loss
        if position > 0 and price <= entry_price * (1 - stop_loss_pct):
            capital += position * price
            position = 0
            entry_price = 0
        # Take-profit
        if position > 0 and price >= entry_price * (1 + take_profit_pct):
            capital += position * price
            position = 0
            entry_price = 0
        portfolio_value = capital + position * price
        history.append({'Date': idx, 'Portfolio Value': portfolio_value})
    return pd.DataFrame(history)


def risk_metrics(portfolio_df):
    returns = portfolio_df['Portfolio Value'].pct_change().dropna()
    sharpe = returns.mean() / returns.std() * (252 ** 0.5)
    cum_max = portfolio_df['Portfolio Value'].cummax()
    drawdown = (portfolio_df['Portfolio Value'] - cum_max) / cum_max
    max_drawdown = drawdown.min()
    return {
        'Sharpe Ratio': sharpe,
        'Max Drawdown': max_drawdown,
        'Total Return': portfolio_df['Portfolio Value'].iloc[-1] / portfolio_df['Portfolio Value'].iloc[0] - 1
    }
