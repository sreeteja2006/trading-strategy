#!/usr/bin/env python3
"""
Trading Interface - Execute trades and manage your trading strategy
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import yfinance as yf
from datetime import datetime, timedelta
import time

st.set_page_config(
    page_title="Trading Interface",
    page_icon="🚀",
    layout="wide"
)

def main():
    st.title("🚀 Trading Interface")
    
    # Trading mode selection
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.info("📝 Demo Mode: Paper trading with virtual money")
    
    with col2:
        if st.button("🔄 Refresh Data"):
            st.rerun()
    
    # Trading controls
    st.subheader("📊 Trading Controls")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        symbol = st.selectbox(
            "Select Stock",
            ["RELIANCE.NS", "TCS.NS", "INFY.NS", "HDFCBANK.NS", "ICICIBANK.NS"],
            key="symbol_select"
        )
    
    with col2:
        action = st.selectbox("Action", ["BUY", "SELL"])
    
    with col3:
        quantity = st.number_input("Quantity", min_value=1, value=10, step=1)
    
    # Get current price
    try:
        ticker = yf.Ticker(symbol)
        data = ticker.history(period="1d")
        if not data.empty:
            current_price = data['Close'].iloc[-1]
            st.metric("Current Price", f"₹{current_price:.2f}")
            
            # Calculate order value
            order_value = current_price * quantity
            st.metric("Order Value", f"₹{order_value:,.2f}")
        else:
            current_price = 0
            st.error("Unable to fetch current price")
    except:
        current_price = 0
        st.error("Error fetching stock data")
    
    # Execute trade button
    if st.button(f"🎯 Execute {action} Order", type="primary"):
        if current_price > 0:
            # Simulate trade execution
            with st.spinner("Executing trade..."):
                time.sleep(1)  # Simulate processing time
            
            st.success(f"✅ {action} order executed successfully!")
            st.info(f"📋 Order Details:\\n"
                   f"- Symbol: {symbol}\\n"
                   f"- Action: {action}\\n"
                   f"- Quantity: {quantity}\\n"
                   f"- Price: ₹{current_price:.2f}\\n"
                   f"- Total: ₹{order_value:,.2f}")
        else:
            st.error("Cannot execute trade - invalid price data")
    
    # Portfolio overview
    st.subheader("💼 Portfolio Overview")
    
    # Mock portfolio data
    portfolio_data = {
        'RELIANCE': {'shares': 100, 'avg_price': 2450, 'current_price': 2475, 'pnl': 2500},
        'TCS': {'shares': 50, 'avg_price': 3500, 'current_price': 3560, 'pnl': 3000},
        'INFY': {'shares': 200, 'avg_price': 1800, 'current_price': 1825, 'pnl': 5000}
    }
    
    # Portfolio metrics
    col1, col2, col3, col4 = st.columns(4)
    
    total_value = sum(pos['shares'] * pos['current_price'] for pos in portfolio_data.values())
    total_pnl = sum(pos['pnl'] for pos in portfolio_data.values())
    cash_balance = 250000
    
    with col1:
        st.metric("Portfolio Value", f"₹{total_value:,.2f}")
    
    with col2:
        st.metric("Cash Balance", f"₹{cash_balance:,.2f}")
    
    with col3:
        st.metric("Total P&L", f"₹{total_pnl:+,.2f}")
    
    with col4:
        st.metric("Positions", len(portfolio_data))
    
    # Current positions table
    st.subheader("📋 Current Positions")
    
    positions_list = []
    for symbol, pos in portfolio_data.items():
        market_value = pos['shares'] * pos['current_price']
        pnl_pct = (pos['pnl'] / (pos['shares'] * pos['avg_price'])) * 100
        
        positions_list.append({
            'Symbol': symbol.replace('.NS', ''),
            'Shares': pos['shares'],
            'Avg Price': f"₹{pos['avg_price']:.2f}",
            'Current Price': f"₹{pos['current_price']:.2f}",
            'Market Value': f"₹{market_value:,.2f}",
            'P&L': f"₹{pos['pnl']:+,.2f}",
            'P&L %': f"{pnl_pct:+.2f}%"
        })
    
    df_positions = pd.DataFrame(positions_list)
    st.dataframe(df_positions, use_container_width=True)
    
    # Trading signals
    st.subheader("📈 Trading Signals")
    
    # Mock signals
    signals_data = [
        {'Symbol': 'RELIANCE', 'Signal': 'BUY', 'Confidence': '75%', 'Reason': 'RSI Oversold + Volume Spike'},
        {'Symbol': 'TCS', 'Signal': 'HOLD', 'Confidence': '45%', 'Reason': 'Neutral indicators'},
        {'Symbol': 'INFY', 'Signal': 'SELL', 'Confidence': '68%', 'Reason': 'RSI Overbought'},
        {'Symbol': 'HDFCBANK', 'Signal': 'BUY', 'Confidence': '82%', 'Reason': 'Bullish breakout'},
    ]
    
    for signal in signals_data:
        col1, col2, col3, col4 = st.columns([2, 1, 1, 3])
        
        with col1:
            st.write(f"**{signal['Symbol']}**")
        
        with col2:
            if signal['Signal'] == 'BUY':
                st.success(signal['Signal'])
            elif signal['Signal'] == 'SELL':
                st.error(signal['Signal'])
            else:
                st.info(signal['Signal'])
        
        with col3:
            st.write(signal['Confidence'])
        
        with col4:
            st.write(signal['Reason'])
    
    # Recent trades
    st.subheader("📝 Recent Trades")
    
    recent_trades = [
        {'Time': '14:30:15', 'Symbol': 'RELIANCE', 'Action': 'BUY', 'Qty': 50, 'Price': '₹2,475.00', 'Status': 'Executed'},
        {'Time': '13:45:22', 'Symbol': 'TCS', 'Action': 'SELL', 'Qty': 25, 'Price': '₹3,560.00', 'Status': 'Executed'},
        {'Time': '12:15:08', 'Symbol': 'INFY', 'Action': 'BUY', 'Qty': 100, 'Price': '₹1,825.00', 'Status': 'Executed'},
        {'Time': '11:30:45', 'Symbol': 'HDFCBANK', 'Action': 'BUY', 'Qty': 30, 'Price': '₹1,650.00', 'Status': 'Executed'},
    ]
    
    df_trades = pd.DataFrame(recent_trades)
    st.dataframe(df_trades, use_container_width=True)
    
    # Risk management
    st.subheader("⚠️ Risk Management")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Daily P&L", "₹+5,250", "0.42%")
        st.progress(0.42)
    
    with col2:
        st.metric("Position Limit", "3/5", "60%")
        st.progress(0.6)
    
    with col3:
        st.metric("Risk Level", "Low", "Safe")
        st.progress(0.3)
    
    # Footer
    st.markdown("---")
    st.markdown("⚠️ **Disclaimer**: This is a demo interface. No real trades are executed.")

if __name__ == "__main__":
    main()