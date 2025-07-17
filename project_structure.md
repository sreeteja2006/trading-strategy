# Organized Project Structure

```
trading-strategy-system/
├── README.md
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .gitignore
├── config/
│   ├── trading_config.json
│   └── risk_config.json
├── src/
│   ├── __init__.py
│   ├── data/
│   │   ├── __init__.py
│   │   ├── data_collector.py
│   │   └── preprocessor.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── prophet_model.py
│   │   ├── arima_model.py
│   │   ├── lstm_model.py
│   │   └── random_forest_model.py
│   ├── strategy/
│   │   ├── __init__.py
│   │   ├── signal_generator.py
│   │   └── backtester.py
│   ├── trading/
│   │   ├── __init__.py
│   │   ├── paper_trader.py
│   │   ├── broker_interface.py
│   │   └── order_manager.py
│   ├── risk/
│   │   ├── __init__.py
│   │   └── risk_manager.py
│   └── utils/
│       ├── __init__.py
│       ├── logger.py
│       └── helpers.py
├── apps/
│   ├── dashboard.py
│   ├── performance_dashboard.py
│   └── trading_interface.py
├── scripts/
│   ├── run_strategy.py
│   ├── run_backtest.py
│   ├── run_paper_trading.py
│   └── demo.py
├── tests/
│   ├── __init__.py
│   ├── test_models.py
│   ├── test_strategy.py
│   └── test_risk.py
├── data/
│   ├── raw/
│   ├── processed/
│   └── results/
├── logs/
└── docs/
    ├── architecture.md
    ├── api_reference.md
    └── user_guide.md
```