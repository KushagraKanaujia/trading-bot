# Getting Started

## Quick Start Guide

This guide will help you get your trading bot up and running in under 10 minutes.

## Prerequisites

Before you begin, make sure you have:
- Python 3.10 or higher installed
- An Alpaca Markets account ([Sign up here](https://alpaca.markets))
- Basic knowledge of Python and trading concepts

## Installation Steps

### 1. Clone the Repository

```bash
git clone https://github.com/KushagraKanaujia/trading-bot.git
cd trading-bot
```

### 2. Run Automated Setup

The setup script will:
- Create a virtual environment
- Install all dependencies
- Check for PostgreSQL and Redis
- Set up your configuration

```bash
chmod +x setup.sh
./setup.sh
```

### 3. Configure Your Environment

Copy the example environment file and add your API keys:

```bash
cp .env.example .env
nano .env  # or use your preferred editor
```

Required settings:
```env
APCA_API_KEY_ID=your_alpaca_key_here
APCA_API_SECRET_KEY=your_alpaca_secret_here
```

### 4. Initialize Database

Create the database tables:

```bash
python init_db.py
```

You should see:
```
✓ Database initialized successfully!
Tables created: trades, positions, price_history, performance_metrics, ml_models
```

### 5. Run the Example

Test that everything works:

```bash
python examples/basic_usage.py
```

Expected output:
```
Trading Bot - Basic Usage Example
==================================================
✓ Risk Manager initialized
✓ Recommended position size for AAPL: 11 shares
✓ Trade APPROVED
...
```

## Next Steps

### Run Tests

Verify all components work correctly:

```bash
pytest
```

For coverage report:
```bash
pytest --cov=src --cov-report=html
```

### Review Risk Settings

Edit `.env` to adjust risk parameters:

```env
MAX_POSITION_SIZE=0.02          # Start with 2% max
STOP_LOSS_PERCENTAGE=0.02       # 2% stop-loss
DAILY_LOSS_LIMIT=0.05           # 5% daily limit
```

### Paper Trading

1. Verify you're using paper trading URL in `.env`:
   ```env
   APCA_API_BASE_URL=https://paper-api.alpaca.markets
   ```

2. Monitor your paper trades on [Alpaca Dashboard](https://app.alpaca.markets/paper/dashboard)

3. Run for at least 3 months before considering live trading

## Common Issues

### "Module not found" Error

Add the project to your Python path:
```bash
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Database Connection Error

Make sure PostgreSQL is running:
```bash
pg_isready
```

Or use SQLite (default):
```env
DATABASE_URL=sqlite:///trading_bot.db
```

### Import Errors

Reinstall dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
trading-bot/
├── src/              # Source code
│   ├── config/       # Configuration
│   ├── models/       # Database models
│   ├── risk/         # Risk management
│   └── ...
├── tests/            # Test suite
├── examples/         # Usage examples
└── docs/             # Documentation
```

## Learning Resources

- [Risk Management Guide](RISK_MANAGEMENT.md)
- [Example Scripts](../examples/)
- [Test Suite](../tests/)

## Support

If you encounter issues:
1. Check this guide
2. Review the main [README](../README.md)
3. Check [GitHub Issues](https://github.com/KushagraKanaujia/trading-bot/issues)

## Safety First

⚠️ **Important Reminders**:
- Always use paper trading first
- Test for at least 3 months
- Start with small position sizes
- Monitor daily
- Never risk money you can't afford to lose

---

Ready to build your first strategy? Check out the [Strategy Guide](STRATEGIES.md)!
