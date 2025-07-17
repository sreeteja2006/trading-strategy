"""
Technical Indicators Module

This module provides various technical analysis indicators commonly used in trading strategies.
Includes trend, momentum, volatility, and volume indicators.
"""

import pandas as pd
import numpy as np
from typing import Tuple, Optional
import logging

logger = logging.getLogger(__name__)


class TechnicalIndicators:
    """
    Collection of technical analysis indicators for stock market data.
    """
    
    @staticmethod
    def simple_moving_average(data: pd.Series, window: int) -> pd.Series:
        """
        Calculate Simple Moving Average (SMA).
        
        Args:
            data: Price series (typically Close prices)
            window: Number of periods for the moving average
            
        Returns:
            Series with SMA values
        """
        return data.rolling(window=window).mean()
    
    @staticmethod
    def exponential_moving_average(data: pd.Series, window: int) -> pd.Series:
        """
        Calculate Exponential Moving Average (EMA).
        
        Args:
            data: Price series
            window: Number of periods
            
        Returns:
            Series with EMA values
        """
        return data.ewm(span=window).mean()
    
    @staticmethod
    def relative_strength_index(data: pd.Series, window: int = 14) -> pd.Series:
        """
        Calculate Relative Strength Index (RSI).
        
        Args:
            data: Price series
            window: Period for RSI calculation (default 14)
            
        Returns:
            Series with RSI values (0-100)
        """
        delta = data.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=window).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=window).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi
    
    @staticmethod
    def macd(data: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate MACD (Moving Average Convergence Divergence).
        
        Args:
            data: Price series
            fast: Fast EMA period (default 12)
            slow: Slow EMA period (default 26)
            signal: Signal line EMA period (default 9)
            
        Returns:
            Tuple of (MACD line, Signal line, Histogram)
        """
        ema_fast = data.ewm(span=fast).mean()
        ema_slow = data.ewm(span=slow).mean()
        
        macd_line = ema_fast - ema_slow
        signal_line = macd_line.ewm(span=signal).mean()
        histogram = macd_line - signal_line
        
        return macd_line, signal_line, histogram
    
    @staticmethod
    def bollinger_bands(data: pd.Series, window: int = 20, num_std: float = 2) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """
        Calculate Bollinger Bands.
        
        Args:
            data: Price series
            window: Period for moving average (default 20)
            num_std: Number of standard deviations (default 2)
            
        Returns:
            Tuple of (Upper band, Middle band/SMA, Lower band)
        """
        sma = data.rolling(window=window).mean()
        std = data.rolling(window=window).std()
        
        upper_band = sma + (std * num_std)
        lower_band = sma - (std * num_std)
        
        return upper_band, sma, lower_band
    
    @staticmethod
    def stochastic_oscillator(high: pd.Series, low: pd.Series, close: pd.Series, 
                            k_window: int = 14, d_window: int = 3) -> Tuple[pd.Series, pd.Series]:
        """
        Calculate Stochastic Oscillator.
        
        Args:
            high: High price series
            low: Low price series
            close: Close price series
            k_window: Period for %K calculation (default 14)
            d_window: Period for %D smoothing (default 3)
            
        Returns:
            Tuple of (%K, %D)
        """
        lowest_low = low.rolling(window=k_window).min()
        highest_high = high.rolling(window=k_window).max()
        
        k_percent = 100 * ((close - lowest_low) / (highest_high - lowest_low))
        d_percent = k_percent.rolling(window=d_window).mean()
        
        return k_percent, d_percent
    
    @staticmethod
    def average_true_range(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
        """
        Calculate Average True Range (ATR).
        
        Args:
            high: High price series
            low: Low price series
            close: Close price series
            window: Period for ATR calculation (default 14)
            
        Returns:
            Series with ATR values
        """
        high_low = high - low
        high_close_prev = np.abs(high - close.shift())
        low_close_prev = np.abs(low - close.shift())
        
        true_range = np.maximum(high_low, np.maximum(high_close_prev, low_close_prev))
        atr = true_range.rolling(window=window).mean()
        
        return atr
    
    @staticmethod
    def commodity_channel_index(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 20) -> pd.Series:
        """
        Calculate Commodity Channel Index (CCI).
        
        Args:
            high: High price series
            low: Low price series
            close: Close price series
            window: Period for CCI calculation (default 20)
            
        Returns:
            Series with CCI values
        """
        typical_price = (high + low + close) / 3
        sma_tp = typical_price.rolling(window=window).mean()
        mean_deviation = typical_price.rolling(window=window).apply(
            lambda x: np.mean(np.abs(x - np.mean(x)))
        )
        
        cci = (typical_price - sma_tp) / (0.015 * mean_deviation)
        
        return cci
    
    @staticmethod
    def williams_percent_r(high: pd.Series, low: pd.Series, close: pd.Series, window: int = 14) -> pd.Series:
        """
        Calculate Williams %R.
        
        Args:
            high: High price series
            low: Low price series
            close: Close price series
            window: Period for calculation (default 14)
            
        Returns:
            Series with Williams %R values
        """
        highest_high = high.rolling(window=window).max()
        lowest_low = low.rolling(window=window).min()
        
        williams_r = -100 * ((highest_high - close) / (highest_high - lowest_low))
        
        return williams_r
    
    @staticmethod
    def on_balance_volume(close: pd.Series, volume: pd.Series) -> pd.Series:
        """
        Calculate On-Balance Volume (OBV).
        
        Args:
            close: Close price series
            volume: Volume series
            
        Returns:
            Series with OBV values
        """
        price_change = close.diff()
        obv = volume.copy()
        
        obv[price_change < 0] = -volume[price_change < 0]
        obv[price_change == 0] = 0
        
        return obv.cumsum()
    
    @staticmethod
    def money_flow_index(high: pd.Series, low: pd.Series, close: pd.Series, 
                        volume: pd.Series, window: int = 14) -> pd.Series:
        """
        Calculate Money Flow Index (MFI).
        
        Args:
            high: High price series
            low: Low price series
            close: Close price series
            volume: Volume series
            window: Period for MFI calculation (default 14)
            
        Returns:
            Series with MFI values
        """
        typical_price = (high + low + close) / 3
        money_flow = typical_price * volume
        
        price_change = typical_price.diff()
        positive_flow = money_flow.where(price_change > 0, 0).rolling(window=window).sum()
        negative_flow = money_flow.where(price_change < 0, 0).rolling(window=window).sum()
        
        money_ratio = positive_flow / negative_flow.abs()
        mfi = 100 - (100 / (1 + money_ratio))
        
        return mfi


def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
    """
    Add all technical indicators to a DataFrame with OHLCV data.
    
    Args:
        df: DataFrame with columns ['Open', 'High', 'Low', 'Close', 'Volume']
        
    Returns:
        DataFrame with additional technical indicator columns
    """
    try:
        indicators = TechnicalIndicators()
        result_df = df.copy()
        
        # Moving Averages
        result_df['SMA_10'] = indicators.simple_moving_average(df['Close'], 10)
        result_df['SMA_20'] = indicators.simple_moving_average(df['Close'], 20)
        result_df['SMA_50'] = indicators.simple_moving_average(df['Close'], 50)
        result_df['EMA_12'] = indicators.exponential_moving_average(df['Close'], 12)
        result_df['EMA_26'] = indicators.exponential_moving_average(df['Close'], 26)
        
        # Momentum Indicators
        result_df['RSI_14'] = indicators.relative_strength_index(df['Close'], 14)
        
        # MACD
        macd, signal, histogram = indicators.macd(df['Close'])
        result_df['MACD'] = macd
        result_df['MACD_Signal'] = signal
        result_df['MACD_Histogram'] = histogram
        
        # Bollinger Bands
        bb_upper, bb_middle, bb_lower = indicators.bollinger_bands(df['Close'])
        result_df['BB_Upper'] = bb_upper
        result_df['BB_Middle'] = bb_middle
        result_df['BB_Lower'] = bb_lower
        
        # Stochastic Oscillator
        stoch_k, stoch_d = indicators.stochastic_oscillator(df['High'], df['Low'], df['Close'])
        result_df['Stoch_K'] = stoch_k
        result_df['Stoch_D'] = stoch_d
        
        # Volatility Indicators
        result_df['ATR_14'] = indicators.average_true_range(df['High'], df['Low'], df['Close'])
        
        # Other Indicators
        result_df['CCI_20'] = indicators.commodity_channel_index(df['High'], df['Low'], df['Close'])
        result_df['Williams_R'] = indicators.williams_percent_r(df['High'], df['Low'], df['Close'])
        
        # Volume Indicators
        if 'Volume' in df.columns:
            result_df['OBV'] = indicators.on_balance_volume(df['Close'], df['Volume'])
            result_df['MFI_14'] = indicators.money_flow_index(df['High'], df['Low'], df['Close'], df['Volume'])
        
        logger.info(f"Added {len(result_df.columns) - len(df.columns)} technical indicators")
        return result_df
        
    except Exception as e:
        logger.error(f"Error adding technical indicators: {str(e)}")
        return df


def main():
    """
    Example usage of technical indicators.
    """
    # Create sample data
    dates = pd.date_range('2023-01-01', periods=100, freq='D')
    np.random.seed(42)
    
    # Generate sample OHLCV data
    close_prices = 100 + np.cumsum(np.random.randn(100) * 0.5)
    high_prices = close_prices + np.random.rand(100) * 2
    low_prices = close_prices - np.random.rand(100) * 2
    open_prices = close_prices + np.random.randn(100) * 0.5
    volumes = np.random.randint(1000, 10000, 100)
    
    sample_data = pd.DataFrame({
        'Date': dates,
        'Open': open_prices,
        'High': high_prices,
        'Low': low_prices,
        'Close': close_prices,
        'Volume': volumes
    })
    sample_data.set_index('Date', inplace=True)
    
    print("Technical Indicators Demo")
    print("=" * 40)
    
    # Add all indicators
    data_with_indicators = add_all_indicators(sample_data)
    
    print(f"Original columns: {len(sample_data.columns)}")
    print(f"With indicators: {len(data_with_indicators.columns)}")
    print(f"Added indicators: {len(data_with_indicators.columns) - len(sample_data.columns)}")
    
    # Show sample of indicators
    print("\nSample Technical Indicators (last 5 rows):")
    indicator_columns = ['Close', 'RSI_14', 'MACD', 'BB_Upper', 'BB_Lower', 'ATR_14']
    print(data_with_indicators[indicator_columns].tail().round(2))


if __name__ == "__main__":
    main()