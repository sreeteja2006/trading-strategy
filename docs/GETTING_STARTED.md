# Getting Started with Trading Strategy Framework

## Prerequisites
- Python 3.10
- Virtual environment
- Basic understanding of financial markets

## Installation
```bash
git clone https://github.com/yourusername/trading-strategy.git
cd trading-strategy
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Basic Usage
1. Configure your strategy:
```python
from scripts import main

# Run with default parameters
main.run(stock="AAPL", start="2023-01-01", end="2024-12-31")

# Custom configuration
main.run(
    stock="AAPL",
    start="2023-01-01",
    end="2024-12-31",
    commission=0.001,
    slippage=0.001,
    initial_capital=100000
)
```

## Next Steps
- See [Configuration Guide](./CONFIGURATION.md) for detailed settings
- Check [Model Documentation](./MODELS.md) for model parameters
- Read [Deployment Guide](./DEPLOYMENT.md) for production setup