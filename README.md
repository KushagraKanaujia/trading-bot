# Trading Bot - Algorithmic Trading Platform

A professional algorithmic trading system with institutional-grade risk management, machine learning capabilities, and comprehensive backtesting.

Built for paper and live trading via Alpaca Markets API.

## Features

### Core Trading System
- **Real-time Trading**: Automated execution via Alpaca Markets
- **Multiple Strategies**: Mean reversion, momentum, ML-based options pricing
- **Risk Management**: Position sizing, stop-loss, portfolio limits
- **Performance Tracking**: Complete trade history and P&L analysis

### Risk Management
- Kelly Criterion position sizing
- Volatility-adjusted sizing (ATR-based)
- Multiple stop-loss types (percentage, trailing, time-based)
- Portfolio exposure limits and correlation analysis
- Value at Risk (VaR) calculation
- Daily loss and drawdown circuit breakers

### Machine Learning
- Neural network for options pricing
- Black-Scholes model comparison
- Feature engineering with technical indicators
- Model versioning and experiment tracking

### Data & Analytics
- PostgreSQL database for persistent storage
- Real-time price tracking and historical data
- Performance metrics (Sharpe ratio, win rate, etc.)
- Trade and position management

## Quick Start

### Prerequisites
- Python 3.10+
- PostgreSQL 14+
- Redis 6+ (optional, for advanced features)
- Alpaca Markets account ([Sign up here](https://alpaca.markets))

### Installation

1. **Clone and setup**:
```bash
git clone https://github.com/KushagraKanaujia/trading-bot.git
cd trading-bot
chmod +x setup.sh
./setup.sh
```

2. **Configure environment**:
```bash
cp .env.example .env
# Edit .env with your Alpaca API keys
```

3. **Initialize database**:
```bash
# Install PostgreSQL
brew install postgresql@14  # macOS
# or
sudo apt-get install postgresql-14  # Ubuntu

# Create database
createdb trading_bot

# Initialize tables
python -c "from src.models import init_db; init_db()"
```

4. **Run tests**:
```bash
pytest tests/ -v
```

## Usage

### Basic Example

```python
from src.risk import RiskManager
from src.config import get_settings

# Initialize risk manager
risk_mgr = RiskManager()

# Calculate position size
size = risk_mgr.calculate_position_size(
    symbol="AAPL",
    price=175.0,
    account_value=100000,
    volatility=2.5  # ATR
)

# Check if trade is allowed
can_trade, reason = risk_mgr.can_open_position(
    symbol="AAPL",
    side="buy",
    proposed_quantity=size,
    price=175.0,
    account_value=100000
)

if can_trade:
    print(f"Trade approved: {size} shares")
else:
    print(f"Trade blocked: {reason}")
```

### Configuration

Edit `.env` to configure risk parameters:

```env
# Position Sizing
MAX_POSITION_SIZE=0.02          # 2% max per trade
MAX_PORTFOLIO_EXPOSURE=0.5      # 50% max total exposure

# Stop Loss
STOP_LOSS_PERCENTAGE=0.02       # 2% stop-loss
TAKE_PROFIT_PERCENTAGE=0.05     # 5% take-profit
TRAILING_STOP_PERCENTAGE=0.03   # 3% trailing stop

# Loss Limits
DAILY_LOSS_LIMIT=0.05           # Halt if daily loss > 5%
MAX_DRAWDOWN_LIMIT=0.15         # Halt if drawdown > 15%
```

## Project Structure

```
trading-bot/
├── src/
│   ├── config/          # Configuration management
│   ├── models/          # Database models
│   ├── risk/            # Risk management system
│   ├── strategies/      # Trading strategies
│   ├── ml/              # Machine learning models
│   ├── data/            # Data fetching
│   ├── execution/       # Order execution
│   └── backtest/        # Backtesting engine
├── tests/               # Test suite
├── .env.example         # Environment template
└── setup.sh             # Automated setup
```

## Testing

Run the test suite:

```bash
# All tests
pytest

# With coverage
pytest --cov=src --cov-report=html

# Specific module
pytest tests/test_risk_manager.py -v
```

## Database Schema

### Trades Table
Stores all executed trades with P&L tracking.

### Positions Table
Current holdings with unrealized P&L.

### Price History Table
Time-series OHLCV data for all tracked symbols.

### Performance Metrics Table
Daily performance statistics and risk metrics.

## Risk Management

The system implements multiple layers of risk control:

1. **Pre-Trade Checks**
   - Position size limits
   - Portfolio exposure limits
   - Correlation checks
   - Daily loss limits

2. **Position Sizing**
   - Kelly Criterion (optimal)
   - Fixed percentage
   - Volatility-adjusted

3. **Exit Management**
   - Stop-loss orders
   - Trailing stops
   - Take-profit targets
   - Time-based exits

4. **Portfolio Monitoring**
   - Value at Risk (VaR)
   - Portfolio beta
   - Maximum drawdown tracking

## Performance Metrics

The system tracks:
- Total P&L (realized and unrealized)
- Sharpe ratio, Sortino ratio, Calmar ratio
- Win rate and profit factor
- Maximum drawdown
- Daily/monthly returns
- Risk-adjusted returns

## Development

### Running Locally

```bash
# Activate virtual environment
source venv/bin/activate

# Start development server
python -m src.api.main

# Run in background
nohup python -m src.api.main > logs/app.log 2>&1 &
```

### Adding New Strategies

Create a new strategy class in `src/strategies/`:

```python
from src.strategies.base import BaseStrategy

class MyStrategy(BaseStrategy):
    def generate_signals(self, data):
        # Your strategy logic here
        pass
```

## Troubleshooting

### Database Connection Issues
```bash
# Check PostgreSQL status
pg_isready

# Test connection
psql trading_bot -c "SELECT 1;"
```

### Module Import Errors
```bash
# Add to PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### Redis Connection (if using)
```bash
# Check Redis
redis-cli ping  # Should return PONG

# Start Redis
redis-server
```

## Deployment

See `docs/DEPLOYMENT.md` for production deployment instructions.

For Heroku deployment:
```bash
heroku create
heroku addons:create heroku-postgresql:standard-0
git push heroku main
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run tests: `pytest`
5. Submit a pull request

## License

MIT License - see LICENSE file for details

## Disclaimer

⚠️ **Trading involves risk of loss.** This software is for educational purposes. Always test thoroughly in paper trading before using real money. Past performance does not guarantee future results.

## Contact

Kushagra Kanaujia - [GitHub](https://github.com/KushagraKanaujia)

Project Link: https://github.com/KushagraKanaujia/trading-bot

---

**Note**: Start with paper trading and test for at least 3 months before considering live trading.
