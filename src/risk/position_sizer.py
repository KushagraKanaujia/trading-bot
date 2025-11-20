"""Position sizing algorithms."""

import logging
from typing import Optional
import math

logger = logging.getLogger(__name__)


class KellyCriterion:
    """Kelly Criterion for optimal position sizing."""

    @staticmethod
    def calculate(win_rate: float, avg_win: float, avg_loss: float, fraction: float = 0.5) -> float:
        """
        Calculate Kelly Criterion percentage.

        Args:
            win_rate: Win rate (0-1)
            avg_win: Average win amount
            avg_loss: Average loss amount (positive number)
            fraction: Kelly fraction (default 0.5 for half-Kelly)

        Returns:
            Position size as fraction of capital (0-1)
        """
        if avg_loss == 0 or win_rate == 0 or win_rate == 1:
            return 0.02  # Default to 2% if invalid inputs

        win_loss_ratio = avg_win / avg_loss
        kelly = (win_rate * win_loss_ratio - (1 - win_rate)) / win_loss_ratio

        # Apply Kelly fraction (half-Kelly for safety)
        kelly = kelly * fraction

        # Cap at 20% for safety
        kelly = max(0, min(kelly, 0.20))

        logger.debug(f"Kelly Criterion: {kelly:.2%} (win_rate={win_rate:.2%}, W/L={win_loss_ratio:.2f})")
        return kelly


class PositionSizer:
    """Calculate optimal position sizes based on various methods."""

    def __init__(self):
        self.kelly = KellyCriterion()

    def calculate_size(
        self,
        price: float,
        account_value: float,
        max_risk_per_trade: float = 0.02,
        volatility: Optional[float] = None,
        win_rate: Optional[float] = None,
        avg_win: Optional[float] = None,
        avg_loss: Optional[float] = None
    ) -> int:
        """
        Calculate position size using multiple methods and choose the most conservative.

        Args:
            price: Current stock price
            account_value: Total account value
            max_risk_per_trade: Maximum risk per trade (default 2%)
            volatility: ATR or volatility measure
            win_rate: Historical win rate
            avg_win: Average win
            avg_loss: Average loss

        Returns:
            Number of shares to buy
        """
        methods = []

        # Method 1: Fixed percentage
        fixed_pct_size = self._fixed_percentage_size(price, account_value, max_risk_per_trade)
        methods.append(('Fixed %', fixed_pct_size))

        # Method 2: Volatility-adjusted (ATR-based)
        if volatility:
            vol_size = self._volatility_adjusted_size(price, account_value, volatility, max_risk_per_trade)
            methods.append(('Volatility', vol_size))

        # Method 3: Kelly Criterion
        if win_rate and avg_win and avg_loss:
            kelly_fraction = self.kelly.calculate(win_rate, avg_win, avg_loss)
            kelly_size = self._kelly_size(price, account_value, kelly_fraction)
            methods.append(('Kelly', kelly_size))

        # Choose the most conservative (smallest) size
        if methods:
            chosen_method, size = min(methods, key=lambda x: x[1])
            logger.info(f"Position sizing methods: {methods}, chose {chosen_method}: {size} shares")
            return max(1, int(size))  # At least 1 share

        return 1

    def _fixed_percentage_size(self, price: float, account_value: float, risk_pct: float) -> int:
        """Calculate size based on fixed percentage of account."""
        position_value = account_value * risk_pct
        return int(position_value / price)

    def _volatility_adjusted_size(
        self,
        price: float,
        account_value: float,
        volatility: float,
        max_risk: float
    ) -> int:
        """
        Calculate size adjusted for volatility (ATR-based).

        Higher volatility = smaller position size
        """
        if volatility == 0:
            return self._fixed_percentage_size(price, account_value, max_risk)

        # Risk amount in dollars
        risk_amount = account_value * max_risk

        # Position size = Risk Amount / (2 * ATR)
        # Using 2x ATR as stop distance
        shares = risk_amount / (2 * volatility)

        return int(shares)

    def _kelly_size(self, price: float, account_value: float, kelly_fraction: float) -> int:
        """Calculate size using Kelly Criterion."""
        position_value = account_value * kelly_fraction
        return int(position_value / price)
