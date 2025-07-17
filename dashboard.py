#!/usr/bin/env python3
"""
Web dashboard for trading strategy
"""
import streamlit as st
import sys
sys.path.append('scripts')

import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import yfinance as yf

st.set_page_config(
    page_title="Trading Strategy Dashboard",
    page_icon="📈",
    layout="wide"
)

def main():
    st.title("📈 Trading Strategy Dashboard")
    st.sidebar.title("Controls")
    
    # Sidebar controls
    symbol = st.sidebar.selectbox("Select Stock", ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS"])
    period = st.sidebar.selectbox("Time Period", ["1mo", "3mo", "6mo", "1y", "2y"])
    
    if st.sidebar.button("🔄 Refresh Data"):
        st.rerun()
    
    # Main dashboard
    col1, col2, col3, col4 = st.columns(4)
    
    try:
        # Get stock data
        ticker = yf.Ticker(symbol)
        data = ticker.history(period=period)
        
        if not data.empty:
            current_price = data['Close'].iloc[-1]
            prev_price = data['Close'].iloc[-2]
            change = current_price - prev_price
            change_pct = (change / prev_price) * 100
            
            # Metrics
            with col1:
                st.metric("Current Price", f"₹{current_price:.2f}", f"{change:+.2f}")
            
            with col2:
                st.metric("Change %", f"{change_pct:+.2f}%")
            
            with col3:
                st.metric("Volume", f"{data['Volume'].iloc[-1]:,.0f}")
            
            with col4:
                st.metric("High/Low", f"₹{data['High'].iloc[-1]:.2f} / ₹{data['Low'].iloc[-1]:.2f}")
            
            # Price chart
            st.subheader("📊 Price Chart")
            fig = go.Figure()
            fig.add_trace(go.Candlestick(
                x=data.index,
                open=data['Open'],
                high=data['High'],
                low=data['Low'],
                close=data['Close'],
                name=symbol
            ))
            fig.update_layout(
                title=f"{symbol} Price Chart",
                yaxis_title="Price (₹)",
                xaxis_title="Date",
                height=500
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Volume chart
            st.subheader("📊 Volume Chart")
            fig_vol = px.bar(x=data.index, y=data['Volume'], title="Trading Volume")
            fig_vol.update_layout(height=300)
            st.plotly_chart(fig_vol, use_container_width=True)
            
            # Technical indicators
            st.subheader("🔧 Technical Analysis")
            
            # Calculate RSI
            delta = data['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs))
            
            col1, col2 = st.columns(2)
            
            with col1:
                st.metric("RSI (14)", f"{rsi.iloc[-1]:.2f}")
                if rsi.iloc[-1] < 30:
                    st.success("🟢 Oversold - Potential Buy")
                elif rsi.iloc[-1] > 70:
                    st.error("🔴 Overbought - Potential Sell")
                else:
                    st.info("🟡 Neutral")
            
            with col2:
                # Simple moving averages
                sma_20 = data['Close'].rolling(20).mean().iloc[-1]
                sma_50 = data['Close'].rolling(50).mean().iloc[-1]
                
                st.metric("SMA 20", f"₹{sma_20:.2f}")
                st.metric("SMA 50", f"₹{sma_50:.2f}")
                
                if current_price > sma_20 > sma_50:
                    st.success("🟢 Bullish Trend")
                elif current_price < sma_20 < sma_50:
                    st.error("🔴 Bearish Trend")
                else:
                    st.info("🟡 Mixed Signals")
            
            # Recent data table
            st.subheader("📋 Recent Data")
            recent_data = data.tail(10)[['Open', 'High', 'Low', 'Close', 'Volume']]
            recent_data = recent_data.round(2)
            st.dataframe(recent_data, use_container_width=True)
            
        else:
            st.error("No data available for the selected symbol")
            
    except Exception as e:
        st.error(f"Error loading data: {e}")
    
    # Footer
    st.markdown("---")
    st.markdown("💡 **Tip**: Use this dashboard to monitor your trading strategy in real-time!")

if __name__ == "__main__":
    main()