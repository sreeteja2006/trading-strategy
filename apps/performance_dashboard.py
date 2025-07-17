#!/usr/bin/env python3
"""
Performance Dashboard - Track your trading strategy results
"""
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
import json
import os
# from paper_trading import PaperTradingAccount

st.set_page_config(
    page_title="Trading Performance Dashboard",
    page_icon="💰",
    layout="wide"
)

def main():
    st.title("💰 Trading Performance Dashboard")
    
    # Mock data for demo purposes
    st.info("📝 Demo Mode: Showing sample trading performance data")
    
    # Mock portfolio summary
    summary = {
        'total_portfolio_value': 1250000,
        'total_return': 50000,
        'total_return_pct': 4.17,
        'cash_balance': 250000,
        'positions': {
            'RELIANCE': {'shares': 100, 'avg_price': 2450, 'current_price': 2475, 'market_value': 247500, 'pnl': 2500, 'pnl_pct': 1.02},
            'TCS': {'shares': 50, 'avg_price': 3500, 'current_price': 3560, 'market_value': 178000, 'pnl': 3000, 'pnl_pct': 1.71},
            'INFY': {'shares': 200, 'avg_price': 1800, 'current_price': 1825, 'market_value': 365000, 'pnl': 5000, 'pnl_pct': 1.39}
        }
    }
    
    # Top metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Portfolio Value", 
            f"₹{summary['total_portfolio_value']:,.2f}",
            f"₹{summary['total_return']:+,.2f}"
        )
    
    with col2:
        st.metric(
            "Total Return", 
            f"{summary['total_return_pct']:+.2f}%"
        )
    
    with col3:
        st.metric(
            "Cash Balance", 
            f"₹{summary['cash_balance']:,.2f}"
        )
    
    with col4:
        st.metric(
            "Active Positions", 
            len(summary['positions'])
        )
    
    # Portfolio composition
    if summary['positions']:
        st.subheader("📊 Portfolio Composition")
        
        # Create pie chart
        symbols = list(summary['positions'].keys())
        values = [pos['market_value'] for pos in summary['positions'].values()]
        
        fig_pie = go.Figure(data=[go.Pie(
            labels=symbols, 
            values=values,
            hole=0.3
        )])
        fig_pie.update_layout(title="Portfolio Allocation")
        st.plotly_chart(fig_pie, use_container_width=True)
        
        # Positions table
        st.subheader("📋 Current Positions")
        positions_data = []
        
        for symbol, pos in summary['positions'].items():
            positions_data.append({
                'Symbol': symbol,
                'Shares': pos['shares'],
                'Avg Price': f"₹{pos['avg_price']:.2f}",
                'Current Price': f"₹{pos['current_price']:.2f}",
                'Market Value': f"₹{pos['market_value']:,.2f}",
                'P&L': f"₹{pos['pnl']:+,.2f}",
                'P&L %': f"{pos['pnl_pct']:+.2f}%"
            })
        
        df_positions = pd.DataFrame(positions_data)
        st.dataframe(df_positions, use_container_width=True)
    
    # Transaction history (mock data)
    st.subheader("📝 Recent Transactions")
    
    # Mock transaction data
    transactions_data = [
        {'Date': '2025-01-17', 'Time': '09:15:00', 'Action': 'BUY', 'Symbol': 'RELIANCE', 'Shares': 100, 'Price': '₹2,450.00', 'Total': '₹2,45,000', 'Balance After': '₹7,55,000'},
        {'Date': '2025-01-16', 'Time': '14:30:00', 'Action': 'BUY', 'Symbol': 'TCS', 'Shares': 50, 'Price': '₹3,500.00', 'Total': '₹1,75,000', 'Balance After': '₹10,00,000'},
        {'Date': '2025-01-15', 'Time': '11:45:00', 'Action': 'SELL', 'Symbol': 'INFY', 'Shares': 25, 'Price': '₹1,820.00', 'Total': '₹45,500', 'Balance After': '₹11,75,000'},
        {'Date': '2025-01-14', 'Time': '10:20:00', 'Action': 'BUY', 'Symbol': 'INFY', 'Shares': 200, 'Price': '₹1,800.00', 'Total': '₹3,60,000', 'Balance After': '₹11,30,000'},
    ]
    
    df_transactions = pd.DataFrame(transactions_data)
    st.dataframe(df_transactions, use_container_width=True)
    
    # Transaction summary
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Total Transactions", "15")
        st.metric("Buy Orders", "9")
        st.metric("Sell Orders", "6")
    
    with col2:
        st.metric("Total Invested", "₹8,50,000")
        st.metric("Total Proceeds", "₹2,15,000")
    
    # Performance chart (if we have historical data)
    st.subheader("📈 Performance Over Time")
    
    # Create sample performance data
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    initial_balance = 1200000
    portfolio_values = [initial_balance + (i * 1000) + (i % 7 * 500) for i in range(len(dates))]
    
    fig_performance = go.Figure()
    fig_performance.add_trace(go.Scatter(
        x=dates,
        y=portfolio_values,
        mode='lines',
        name='Portfolio Value',
        line=dict(color='green', width=2)
    ))
    
    fig_performance.add_hline(
        y=initial_balance, 
        line_dash="dash", 
        line_color="red",
        annotation_text="Initial Balance"
    )
    
    fig_performance.update_layout(
        title="Portfolio Value Over Time",
        xaxis_title="Date",
        yaxis_title="Portfolio Value (₹)",
        height=400
    )
    
    st.plotly_chart(fig_performance, use_container_width=True)
    
    # Strategy statistics
    st.subheader("📊 Strategy Statistics")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric("Win Rate", "65%")  # You'd calculate this from actual trades
        st.metric("Avg Trade Return", "+2.3%")
    
    with col2:
        st.metric("Best Trade", "+₹1,250")
        st.metric("Worst Trade", "-₹850")
    
    with col3:
        st.metric("Sharpe Ratio", "1.45")
        st.metric("Max Drawdown", "-3.2%")
    
    # Refresh button
    if st.button("🔄 Refresh Data"):
        st.rerun()
    
    # Footer
    st.markdown("---")
    st.markdown("💡 **Tip**: This is paper trading with virtual money. No real trades are executed!")

if __name__ == "__main__":
    main()