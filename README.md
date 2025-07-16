# Trading Strategy Framework

A comprehensive Python framework for developing, testing, and deploying trading strategies.

## Features
- Multi-model ensemble predictions (LSTM, ARIMA, Prophet, Random Forest)
- Transaction costs and slippage simulation
- Walk-forward analysis and cross-validation
- Automated reporting and notifications
- Support for stocks, crypto, and forex

## Quick Start
```bash
# Install dependencies
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Run strategy
python scripts/main.py --stock AAPL --start 2023-01-01 --end 2024-12-31
```

## Documentation
See the [docs](./docs) folder for detailed documentation.

## Contributing
1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request