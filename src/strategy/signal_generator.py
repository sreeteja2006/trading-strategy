"""
Signal Generator Module

Generates trading signals based on technical indicators and model predictions.
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Optional, Tuple
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class SignalGenerator:
    """
    Generates trading signals based on various strategies and indicators.
    """
    
    def __init__(self):
        self.signals = []
        self.current_position = 0  # 1 for long, -1 for short, 0 for neutral
        
    def generate_ma_crossover_signals(self, data: pd.DataFrame, 
                                    short_window: int = 10, 
                                    long_window: int = 30) -> pd.DataFrame:
        """
        Generate signals based on moving average crossover strategy.
        
        Args:
            data: DataFrame with price data
            short_window: Short-term moving average period
            long_window: Long-term moving average period
            
        Returns:
            DataFrame with signals
        """
        signals_df = data.copy()
        
        # Calculate moving averages
        signals_df['MA_short'] = signals_df['Close'].rolling(window=short_window).mean()
        signals_df['MA_long'] = signals_df['Close'].rolling(window=long_window).mean()
        
        # Generate signals
        signals_df['Signal'] = 0
        signals_df['Signal'][short_window:] = np.where(
            signals_df['MA_short'][short_window:] > signals_df['MA_long'][short_window:], 1, 0
        )
        
        # Generate trading positions
        signals_df['Position'] = signals_df['Signal'].diff()
        
        return signals_df
    
    def generate_rsi_signals(self, data: pd.DataFrame, 
                           rsi_period: int = 14,
                           oversold: int = 30,
                           overbought: int = 70) -> pd.DataFrame:
        """
        Generate signals based on RSI strategy.
        
        Args:
            data: DataFrame with price data
            rsi_period: RSI calculation period
            oversold: Oversold threshold
            overbought: Overbought threshold
            
        Returns:
            DataFrame with RSI signals
        """
        signals_df = data.copy()
        
        # Calculate RSI
        signals_df['RSI'] = self._calculate_rsi(signals_df['Close'], rsi_period)
        
        # Generate signals
        signals_df['Signal'] = 0
        signals_df.loc[signals_df['RSI'] < oversold, 'Signal'] = 1  # Buy signal
        signals_df.loc[signals_df['RSI'] > overbought, 'Signal'] = -1  # Sell signal
        
        return signals_df
    
    def _calculate_rsi(self, prices: pd.Series, period: int = 14) -> pd.Series:
        """Calculate Relative Strength Index."""
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        
        rs = gain / loss
        rsi = 100 - (100 / (1 + rs))
        
        return rsi