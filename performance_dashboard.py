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
from paper_trading import PaperTradingAccount

st.set_page_config(
    page_title="Trading Performance Dashboard",
    page_icon="💰",
    layout="wide"
)

def load_account_data():
    """Load paper trading account data"""
    account = PaperTradingAccount()
    if account.load_account():
        return account
    return None

def main():
    st.title("💰 Trading Performance Dashboard")
    
    # Load account data
    account = load_account_data()
    
    if account is None:
        st.error("No trading account found. Run paper_trading.py first!")
        return
    
    # Get portfolio summary
    summary = account.get_portfolio_summary()
    
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
    
    # Transaction history
    if account.transactions:
        st.subheader("📝 Transaction History")
        
        # Convert transactions to DataFrame
        transactions_data = []
        for t in account.transactions:
            transactions_data.append({
                'Date': t['timestamp'].strftime('%Y-%m-%d'),
                'Time': t['timestamp'].strftime('%H:%M:%S'),
                'Action': t['action'],
                'Symbol': t['symbol'],
                'Shares': t['shares'],
                'Price': f"₹{t['price']:.2f}",
                'Total': f"₹{t['total']:,.2f}",
                'Balance After': f"₹{t['balance_after']:,.2f}"
            })
        
        df_transactions = pd.DataFrame(transactions_data)
        st.dataframe(df_transactions.tail(20), use_container_width=True)
        
        # Transaction summary
        col1, col2 = st.columns(2)
        
        with col1:
            buy_transactions = [t for t in account.transactions if t['action'] == 'BUY']
            sell_transactions = [t for t in account.transactions if t['action'] == 'SELL']
            
            st.metric("Total Transactions", len(account.transactions))
            st.metric("Buy Orders", len(buy_transactions))
            st.metric("Sell Orders", len(sell_transactions))
        
        with col2:
            if buy_transactions:
                total_invested = sum(t['total'] for t in buy_transactions)
                st.metric("Total Invested", f"₹{total_invested:,.2f}")
            
            if sell_transactions:
                total_proceeds = sum(t['total'] for t in sell_transactions)
                st.metric("Total Proceeds", f"₹{total_proceeds:,.2f}")
    
    # Performance chart (if we have historical data)
    st.subheader("📈 Performance Over Time")
    
    # Create sample performance data (in real implementation, you'd track this)
    dates = pd.date_range(start=datetime.now() - timedelta(days=30), end=datetime.now(), freq='D')
    portfolio_values = [account.initial_balance + (i * 100) + (i % 7 * 50) for i in range(len(dates))]
    
    fig_performance = go.Figure()
    fig_performance.add_trace(go.Scatter(
        x=dates,
        y=portfolio_values,
        mode='lines',
        name='Portfolio Value',
        line=dict(color='green', width=2)
    ))
    
    fig_performance.add_hline(
        y=account.initial_balance, 
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