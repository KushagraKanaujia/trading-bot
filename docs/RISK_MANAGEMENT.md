# Risk Management System

## Overview

The trading bot includes a comprehensive 4-layer risk management system designed to protect capital and limit losses.

## Components

### 1. Position Sizing

**Kelly Criterion**
- Mathematically optimal position sizing
- Based on win rate and win/loss ratio
- Uses fractional Kelly (50%) for safety
- Capped at 20% maximum

**Volatility-Adjusted**
- Dynamic sizing based on ATR (Average True Range)
- Smaller positions in volatile stocks
- Larger positions in stable stocks

**Fixed Percentage**
- Simple percentage-based sizing
- Default: 2% of account per trade

### 2. Stop-Loss Management

**Percentage-Based Stops**
- Default: 2% stop-loss
- Configurable per strategy

**Trailing Stops**
- Default: 3% trailing distance
- Locks in profits as price moves
- Only moves up, never down (for longs)

**Time-Based Stops**
- Exit if position held too long without profit
- Default: 24 hours

**Take-Profit Targets**
- Default: 5% profit target
- Automatic profit-taking

### 3. Portfolio Limits

**Exposure Limits**
- Maximum 50% total portfolio exposure
- Maximum 2% per single position

**Correlation Analysis**
- Prevents over-concentrated positions
- Max correlation: 0.7 with existing positions

**Daily Loss Limit**
- Trading halts if daily loss exceeds 5%
- Circuit breaker protection

**Maximum Drawdown**
- Trading halts if drawdown exceeds 15%
- Protects against catastrophic losses

### 4. Risk Metrics

**Value at Risk (VaR)**
- Historical method
- 95% confidence level
- Estimates potential daily loss

**Portfolio Beta**
- Measures market correlation
- Benchmarked to SPY
- Uses 90-day returns

## Configuration

Edit `.env` to adjust risk parameters:

```env
MAX_POSITION_SIZE=0.02          # 2% max per trade
MAX_PORTFOLIO_EXPOSURE=0.5      # 50% max total
STOP_LOSS_PERCENTAGE=0.02       # 2% stop-loss
TAKE_PROFIT_PERCENTAGE=0.05     # 5% take-profit
DAILY_LOSS_LIMIT=0.05           # 5% daily limit
MAX_DRAWDOWN_LIMIT=0.15         # 15% max drawdown
```

## Usage Example

```python
from src.risk import RiskManager

risk_mgr = RiskManager()

# Calculate position size
size = risk_mgr.calculate_position_size(
    symbol="AAPL",
    price=175.0,
    account_value=100000,
    volatility=2.5,
    win_rate=0.55,
    avg_win=150,
    avg_loss=100
)

# Check if trade allowed
can_trade, reason = risk_mgr.can_open_position(
    symbol="AAPL",
    side="buy",
    proposed_quantity=size,
    price=175.0,
    account_value=100000
)

# Monitor position
should_exit, exit_reason = risk_mgr.should_exit_position(
    symbol="AAPL",
    entry_price=175.0,
    current_price=172.0,
    quantity=size,
    side="buy"
)
```

## Best Practices

1. **Start Conservative**
   - Use 1% position size initially
   - Increase gradually as system proves itself

2. **Monitor Daily**
   - Check risk summary every day
   - Review all trades and exits

3. **Adjust Parameters**
   - Tune based on strategy performance
   - Consider market conditions

4. **Test Thoroughly**
   - Paper trade for 3+ months
   - Verify all risk controls work

## Safety Features

- ✓ Pre-trade risk checks
- ✓ Automatic stop-losses
- ✓ Portfolio exposure limits
- ✓ Daily loss circuit breakers
- ✓ Correlation monitoring
- ✓ Real-time risk metrics
