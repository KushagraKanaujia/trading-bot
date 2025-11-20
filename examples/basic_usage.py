"""Basic usage example for the trading bot."""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.risk import RiskManager
from src.config import get_settings


def main():
    """Demonstrate basic trading bot usage."""
    print("Trading Bot - Basic Usage Example")
    print("=" * 50)

    # Initialize risk manager
    print("\n1. Initializing Risk Manager...")
    risk_mgr = RiskManager()
    print("✓ Risk Manager initialized")

    # Example 1: Calculate position size
    print("\n2. Calculating Position Size...")
    symbol = "AAPL"
    price = 175.0
    account_value = 100000.0
    volatility = 2.5  # ATR

    size = risk_mgr.calculate_position_size(
        symbol=symbol,
        price=price,
        account_value=account_value,
        volatility=volatility,
        win_rate=0.55,
        avg_win=150,
        avg_loss=100
    )

    print(f"✓ Recommended position size for {symbol}: {size} shares")
    print(f"  Price: ${price}")
    print(f"  Position value: ${size * price:,.2f}")
    print(f"  % of account: {(size * price / account_value) * 100:.2f}%")

    # Example 2: Check if trade is allowed
    print("\n3. Checking Trade Approval...")
    can_trade, reason = risk_mgr.can_open_position(
        symbol=symbol,
        side="buy",
        proposed_quantity=size,
        price=price,
        account_value=account_value
    )

    if can_trade:
        print(f"✓ Trade APPROVED: Can buy {size} shares of {symbol}")
    else:
        print(f"✗ Trade REJECTED: {reason}")

    # Example 3: Check exit conditions
    print("\n4. Checking Exit Conditions...")
    entry_price = 175.0
    current_price = 172.0

    should_exit, exit_reason = risk_mgr.should_exit_position(
        symbol=symbol,
        entry_price=entry_price,
        current_price=current_price,
        quantity=size,
        side="buy"
    )

    if should_exit:
        print(f"✗ EXIT SIGNAL: {exit_reason}")
    else:
        print(f"✓ HOLD: Position within acceptable range")

    pnl_pct = ((current_price - entry_price) / entry_price) * 100
    print(f"  Current P&L: {pnl_pct:+.2f}%")

    # Example 4: Get risk summary
    print("\n5. Risk Summary...")
    try:
        summary = risk_mgr.get_risk_summary()
        print(f"  Portfolio Value: ${summary['portfolio_value']:,.2f}")
        print(f"  Daily P&L: ${summary['daily_pnl']:,.2f} ({summary['daily_pnl_pct']:+.2f}%)")
        print(f"  Current Drawdown: {summary['current_drawdown_pct']:.2f}%")
        print(f"  Exposure: {summary['exposure_pct']:.2f}%")
        print(f"  Can Trade: {'✓ Yes' if summary['can_trade'] else '✗ No'}")
    except Exception as e:
        print(f"  ℹ No historical data available yet")

    print("\n" + "=" * 50)
    print("Example completed successfully!")


if __name__ == "__main__":
    main()
