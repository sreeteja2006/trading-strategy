def generate_signals(forecast, actual_prices, threshold=0.02):
    signals = []
    for f, a in zip(forecast, actual_prices):
        change = (f - a) / a
        if change > threshold:
            signals.append('Buy')
        elif change < -threshold:
            signals.append('Sell')
        else:
            signals.append('Hold')
        return signals