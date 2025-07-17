"""
Data Collection Module

This module handles fetching and preprocessing of market data from various sources.
Primarily uses Yahoo Finance API for real-time and historical stock data.
"""

import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class MarketDataCollector:
    """
    Handles collection of market data from various sources.
    
    Currently supports Yahoo Finance API for Indian stock market data.
    """
    
    def __init__(self):
        self.supported_exchanges = ['NSE', 'BSE']
        self.cache = {}
        
    def fetch_stock_data(self, symbol: str, period: str = "1y", 
                        interval: str = "1d") -> Optional[pd.DataFrame]:
        """
        Fetch historical stock data for a given symbol.
        
        Args:
            symbol: Stock symbol (e.g., 'RELIANCE.NS')
            period: Time period ('1d', '5d', '1mo', '3mo', '6mo', '1y', '2y', '5y', '10y', 'ytd', 'max')
            interval: Data interval ('1m', '2m', '5m', '15m', '30m', '60m', '90m', '1h', '1d', '5d', '1wk', '1mo', '3mo')
            
        Returns:
            DataFrame with OHLCV data or None if failed
        """
        try:
            logger.info(f"Fetching data for {symbol} with period {period}")
            
            ticker = yf.Ticker(symbol)
            data = ticker.history(period=period, interval=interval)
            
            if data.empty:
                logger.warning(f"No data found for symbol {symbol}")
                return None
                
            # Clean and validate data
            data = self._clean_data(data)
            
            # Cache the data
            cache_key = f"{symbol}_{period}_{interval}"
            self.cache[cache_key] = {
                'data': data,
                'timestamp': datetime.now()
            }
            
            logger.info(f"Successfully fetched {len(data)} records for {symbol}")
            return data
            
        except Exception as e:
            logger.error(f"Error fetching data for {symbol}: {str(e)}")
            return None
    
    def fetch_multiple_stocks(self, symbols: List[str], period: str = "1y") -> Dict[str, pd.DataFrame]:
        """
        Fetch data for multiple stocks simultaneously.
        
        Args:
            symbols: List of stock symbols
            period: Time period for data
            
        Returns:
            Dictionary mapping symbols to their data
        """
        results = {}
        
        for symbol in symbols:
            data = self.fetch_stock_data(symbol, period)
            if data is not None:
                results[symbol] = data
                
        logger.info(f"Successfully fetched data for {len(results)}/{len(symbols)} symbols")
        return results
    
    def get_current_price(self, symbol: str) -> Optional[float]:
        """
        Get current market price for a symbol.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Current price or None if failed
        """
        try:
            ticker = yf.Ticker(symbol)
            data = ticker.history(period="1d", interval="1m")
            
            if not data.empty:
                return float(data['Close'].iloc[-1])
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {str(e)}")
            return None
    
    def get_stock_info(self, symbol: str) -> Optional[Dict]:
        """
        Get detailed stock information.
        
        Args:
            symbol: Stock symbol
            
        Returns:
            Dictionary with stock information
        """
        try:
            ticker = yf.Ticker(symbol)
            info = ticker.info
            
            # Extract relevant information
            stock_info = {
                'symbol': symbol,
                'company_name': info.get('longName', 'N/A'),
                'sector': info.get('sector', 'N/A'),
                'industry': info.get('industry', 'N/A'),
                'market_cap': info.get('marketCap', 0),
                'pe_ratio': info.get('trailingPE', 0),
                'dividend_yield': info.get('dividendYield', 0),
                'beta': info.get('beta', 0),
                '52_week_high': info.get('fiftyTwoWeekHigh', 0),
                '52_week_low': info.get('fiftyTwoWeekLow', 0)
            }
            
            return stock_info
            
        except Exception as e:
            logger.error(f"Error getting stock info for {symbol}: {str(e)}")
            return None
    
    def _clean_data(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Clean and validate the fetched data.
        
        Args:
            data: Raw data from API
            
        Returns:
            Cleaned data
        """
        # Remove any rows with all NaN values
        data = data.dropna(how='all')
        
        # Forward fill missing values
        data = data.fillna(method='ffill')
        
        # Ensure all price columns are positive
        price_columns = ['Open', 'High', 'Low', 'Close']
        for col in price_columns:
            if col in data.columns:
                data[col] = data[col].abs()
        
        # Ensure High >= Low
        if 'High' in data.columns and 'Low' in data.columns:
            data['High'] = np.maximum(data['High'], data['Low'])
        
        # Ensure Volume is non-negative
        if 'Volume' in data.columns:
            data['Volume'] = data['Volume'].abs()
        
        return data
    
    def is_market_open(self) -> bool:
        """
        Check if the Indian stock market is currently open.
        
        Returns:
            True if market is open, False otherwise
        """
        now = datetime.now()
        
        # Check if it's a weekend
        if now.weekday() >= 5:  # Saturday = 5, Sunday = 6
            return False
        
        # Market hours: 9:15 AM to 3:30 PM IST
        market_open = now.replace(hour=9, minute=15, second=0, microsecond=0)
        market_close = now.replace(hour=15, minute=30, second=0, microsecond=0)
        
        return market_open <= now <= market_close
    
    def get_cache_info(self) -> Dict:
        """
        Get information about cached data.
        
        Returns:
            Dictionary with cache statistics
        """
        cache_info = {
            'total_cached_items': len(self.cache),
            'cache_keys': list(self.cache.keys()),
            'oldest_cache': None,
            'newest_cache': None
        }
        
        if self.cache:
            timestamps = [item['timestamp'] for item in self.cache.values()]
            cache_info['oldest_cache'] = min(timestamps)
            cache_info['newest_cache'] = max(timestamps)
        
        return cache_info


def main():
    """
    Example usage of the MarketDataCollector class.
    """
    collector = MarketDataCollector()
    
    # Test symbols
    symbols = ['RELIANCE.NS', 'TCS.NS', 'INFY.NS']
    
    print("Market Data Collector Demo")
    print("=" * 40)
    
    # Check if market is open
    market_status = "OPEN" if collector.is_market_open() else "CLOSED"
    print(f"Market Status: {market_status}")
    
    # Fetch data for multiple stocks
    print(f"\nFetching data for {len(symbols)} stocks...")
    data_dict = collector.fetch_multiple_stocks(symbols, period="30d")
    
    for symbol, data in data_dict.items():
        if data is not None:
            current_price = data['Close'].iloc[-1]
            print(f"{symbol}: {len(data)} records, Current Price: ₹{current_price:.2f}")
    
    # Get current prices
    print(f"\nCurrent Prices:")
    for symbol in symbols:
        price = collector.get_current_price(symbol)
        if price:
            print(f"{symbol}: ₹{price:.2f}")
    
    # Cache information
    cache_info = collector.get_cache_info()
    print(f"\nCache Info: {cache_info['total_cached_items']} items cached")


if __name__ == "__main__":
    main()