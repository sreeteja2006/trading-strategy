# 📈 TradePro - Trading Strategy System

> **⚠️ FOR LEARNING ONLY - NOT FOR REAL TRADING**

A trading platform built with Python and Flask that helps you track markets, manage your portfolio, and monitor system performance.

![TradePro Dashboard](https://img.shields.io/badge/TradePro-Dashboard-blue)
![Python 3.9+](https://img.shields.io/badge/Python-3.9%2B-blue)
![Flask](https://img.shields.io/badge/Flask-2.3.3-green)
![Docker](https://img.shields.io/badge/Docker-Ready-blue)
![Render](https://img.shields.io/badge/Render-Deployment-purple)

## 🚀 What is TradePro?

TradePro is a trading platform I built for traders who want to:

- Track stock prices and market trends in real-time
- Keep an eye on their portfolio performance
- Execute trades with built-in risk controls
- Monitor the health of the trading system
- Use a clean, modern interface that works on any device

The system is designed to be easy to use while still offering powerful features for serious traders.

## 🏗️ How It's Built

The system has three main parts:

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Data Layer    │    │  Business Logic │    │    Web Layer    │
│                 │    │                 │    │                 │
│ • Market Data   │───▶│ • Trading Logic │───▶│ • Flask App     │
│ • User Data     │    │ • Risk Mgmt     │    │ • REST APIs     │
│ • System Data   │    │ • Analytics     │    │ • Templates     │
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

I used:
- **Backend**: Python with Flask
- **Frontend**: HTML, CSS, JavaScript with Bootstrap
- **Data**: pandas for analysis, yfinance for market data
- **Charts**: Plotly.js for interactive visualizations
- **Monitoring**: psutil for system stats
- **Deployment**: Docker and Render for easy hosting
- **Storage**: SQLite database for simplicity

## 📊 Main Features

### 1. Trading Dashboard
- Live stock price charts
- Technical indicators like RSI and MACD
- Volume tracking
- Price alerts when stocks hit certain levels

### 2. Performance Dashboard
- See your portfolio breakdown in a pie chart
- Track how your investments are doing over time
- Review your past trades
- Check key stats like win rate and profit/loss

### 3. Trading Interface
- Place buy and sell orders
- Manage your open positions
- Set risk limits to protect your account
- Get trading signals based on technical analysis

### 4. System Status
- Monitor CPU, memory, and disk usage
- Check if all services are running properly
- View system logs if something goes wrong
- Back up your data with one click

### 5. User-Friendly Design
- Works on phones, tablets, and computers
- Dark mode for night trading
- Interactive charts you can zoom and pan
- Real-time updates without refreshing
- Customizable layout

## 🧠 Machine Learning Models & Trading Strategies

TradePro uses several machine learning models to predict market movements and generate trading signals:

### Prophet Model
- **What it is**: A forecasting model created by Facebook that's good at finding patterns in time series data
- **How it works**: It breaks down price data into trend, seasonal patterns, and holiday effects
- **Why it's useful**: It handles missing data well and can spot non-linear trends in stock prices
- **What we adjust**: How sensitive it is to trend changes and how it handles seasonal patterns

### ARIMA Model
- **What it is**: A statistical model that uses past values and errors to predict future prices
- **How it works**: It combines three components - past values (AR), difference between values (I), and moving averages of errors (MA)
- **Why it's useful**: It's good at capturing short-term patterns in stock prices
- **What we adjust**: How many past values to use and how many differences to take

### LSTM Neural Networks
- **What it is**: A special type of neural network that's good at learning patterns in sequence data
- **How it works**: It has "memory cells" that can remember important information and forget irrelevant details
- **Why it's useful**: It can spot complex patterns in stock prices that simpler models might miss
- **What we adjust**: How many layers to use, how many neurons per layer, and how much data to feed it

### Random Forest
- **What it is**: A model that uses many decision trees to make better predictions
- **How it works**: It creates many different decision trees and lets them vote on the best prediction
- **Why it's useful**: It's less likely to overfit and can handle many different types of data
- **What we adjust**: How many trees to use and how deep each tree can grow

### Ensemble Model
- **What it is**: A combination of multiple models to get better predictions
- **How it works**: It takes predictions from all the models above and combines them intelligently
- **Why it's useful**: It usually performs better than any single model alone
- **What we adjust**: How much weight to give each model's prediction

### Feature Engineering
- **What it does**: Creates useful inputs for our models from raw price data
- **Examples**: Technical indicators (RSI, MACD), volatility measures, momentum indicators
- **Why it's useful**: Helps models find patterns that aren't obvious in raw price data

### Reinforcement Learning
- **What it is**: A type of machine learning where an agent learns by interacting with the market
- **How it works**: The agent tries different trading actions and learns from the results
- **Why it's useful**: It can develop complex trading strategies that adapt to changing markets
- **What we adjust**: How to balance immediate profits vs. long-term returns

### Traditional Trading Strategies

Besides machine learning, TradePro also includes traditional trading strategies:

#### Moving Average Strategy
This strategy buys when a short-term average crosses above a long-term average (golden cross) and sells when it crosses below (death cross). It's simple but effective for trending markets.

#### RSI Strategy
The Relative Strength Index measures if a stock is overbought or oversold. This strategy buys when RSI is below 30 (oversold) and sells when it's above 70 (overbought).

#### MACD Strategy
The Moving Average Convergence Divergence looks at the relationship between two moving averages. It generates buy signals when the MACD line crosses above the signal line and sell signals when it crosses below.

#### Bollinger Bands Strategy
This uses a moving average with upper and lower bands that are 2 standard deviations away. It buys when price touches the lower band (potential support) and sells when it touches the upper band (potential resistance).

## 🚀 Getting Started

### What You Need
```bash
Python 3.9 or newer
Docker (optional, for container deployment)
```

### Local Setup
```bash
# Clone the repository
git clone https://github.com/yourusername/tradepro
cd tradepro

# Set up Python environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install required packages
pip install -r requirements.txt

# Run the app
python web_app.py

# Open your browser to http://localhost:5000
```

### Docker Setup
```bash
# Build and run with Docker
docker build -t tradepro .
docker run -p 5000:5000 tradepro

# Or use Docker Compose for an even easier setup
docker-compose up -d
```

### Render Deployment
The app is ready to deploy on Render using the included `render.yaml` file.

## 📊 What's Inside

```
tradepro/
├── apps/                      # Main app modules
│   ├── dashboard.py           # Trading dashboard
│   ├── main.py                # Main router
│   ├── performance_dashboard.py # Performance tracking
│   ├── system_status.py       # System monitoring
│   └── trading_interface.py   # Trading execution
├── config/                    # Settings files
│   ├── risk_config.json       # Risk management settings
│   └── trading_config.json    # Trading parameters
├── data/                      # Data storage
├── static/                    # Web assets (CSS, JS)
├── templates/                 # HTML templates
├── app.py                     # Flask app setup
├── Dockerfile                 # Docker config
├── requirements.txt           # Python dependencies
└── web_app.py                 # Main entry point
```

## 🖥️ What You'll See

### Home Screen
- Overview of your portfolio
- Quick links to all features
- Recent activity feed
- Market alerts
- Upcoming market events

### Trading Dashboard
- Real-time price charts
- Technical indicators
- Buy/sell signals
- Market news

### Performance Dashboard
- Portfolio breakdown
- Performance charts
- Position details
- Trade history
- Strategy stats

### System Status
- CPU, memory, and disk usage
- Service health indicators
- System logs
- Backup tools

## ⚙️ Settings You Can Change

### Trading Settings (config/trading_config.json)
```json
{
  "symbols": [
    "RELIANCE", "TCS", "INFY", "HDFCBANK", "ICICIBANK", 
    "NIFTY50", "NIFTYBANK", "NIFTYMIDCAP", 
    "GOLD", "SILVER", "CRUDEOIL", "NATURALGAS", "COPPER"
  ],
  "max_positions": 8,
  "position_size_pct": 0.1,
  "stop_loss_pct": 0.05,
  "take_profit_pct": 0.15,
  "daily_loss_limit": 0.02,
  "max_trades_per_day": 10
}
```

### Risk Settings (config/risk_config.json)
```json
{
  "max_portfolio_risk": 0.02,
  "max_position_size_pct": 0.2,
  "correlation_threshold": 0.7,
  "max_sector_exposure": 0.3,
  "volatility_threshold": 0.25
}
```

## 🔒 Security Features

- HTTPS support for secure connections
- User authentication
- Input validation
- Protection against common web attacks
- Secure API endpoints

## 🧪 Testing

```bash
# Run tests
python -m unittest discover tests
```

## 📱 Works on All Devices

TradePro works great on:
- Desktop computers
- Laptops
- Tablets
- Mobile phones

The interface automatically adjusts to fit your screen size.

## 🌙 Dark Mode

TradePro includes a dark mode that:
- Is easier on your eyes during night trading
- Saves battery on phones and tablets
- Looks modern and professional
- Remembers your preference

## 🔧 Make It Your Own

You can customize:
- Dashboard layout
- Chart types and indicators
- Color themes
- Alert settings
- Data refresh timing

## ⚠️ Important Notes

- **For Learning Only**: This project is for education and practice
- **Not Financial Advice**: Don't use for real trading decisions
- **No Guarantees**: Past performance doesn't predict future results
- **Trading is Risky**: You can lose money trading stocks

## 📞 Contact

- **GitHub**: sreeteja2006
- **Email**: gsreeteja25@gmail.com

---

**Built with ❤️ using Python, Flask, and modern web tools**