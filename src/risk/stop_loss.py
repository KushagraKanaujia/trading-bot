"""Stop-loss and take-profit management."""

import logging
from typing import Optional, Dict
from datetime import datetime, timedelta

from src.config import get_settings

logger = logging.getLogger(__name__)


class StopLossManager:
    """Manage stop-loss and take-profit levels."""

    def __init__(self):
        self.settings = get_settings()
        self.trailing_stops: Dict[str, float] = {}  # symbol -> stop price
        self.entry_times: Dict[str, datetime] = {}  # symbol -> entry time

    def should_exit(
        self,
        entry_price: float,
        current_price: float,
        quantity: float,
        side: str
    ) -> tuple[bool, Optional[str]]:
        """
        Determine if position should be exited based on stop-loss/take-profit.

        Returns:
            tuple: (should_exit, reason)
        """
        if side.lower() == "buy" or side.lower() == "long":
            return self._check_long_exit(entry_price, current_price)
        else:
            return self._check_short_exit(entry_price, current_price)

    def _check_long_exit(self, entry_price: float, current_price: float) -> tuple[bool, Optional[str]]:
        """Check exit conditions for long positions."""
        # Calculate P&L percentage
        pnl_pct = (current_price - entry_price) / entry_price

        # Check stop-loss
        if pnl_pct <= -self.settings.stop_loss_percentage:
            logger.info(f"Stop-loss triggered at {pnl_pct:.2%}")
            return True, f"Stop-loss triggered ({pnl_pct:.2%})"

        # Check take-profit
        if pnl_pct >= self.settings.take_profit_percentage:
            logger.info(f"Take-profit triggered at {pnl_pct:.2%}")
            return True, f"Take-profit reached ({pnl_pct:.2%})"

        return False, None

    def _check_short_exit(self, entry_price: float, current_price: float) -> tuple[bool, Optional[str]]:
        """Check exit conditions for short positions."""
        # For shorts, profit when price goes down
        pnl_pct = (entry_price - current_price) / entry_price

        # Check stop-loss (price going up)
        if pnl_pct <= -self.settings.stop_loss_percentage:
            logger.info(f"Stop-loss triggered at {pnl_pct:.2%}")
            return True, f"Stop-loss triggered ({pnl_pct:.2%})"

        # Check take-profit (price going down)
        if pnl_pct >= self.settings.take_profit_percentage:
            logger.info(f"Take-profit triggered at {pnl_pct:.2%}")
            return True, f"Take-profit reached ({pnl_pct:.2%})"

        return False, None

    def update_trailing_stop(self, symbol: str, current_price: float):
        """
        Update trailing stop for a symbol.

        Trailing stop only moves up (for longs), never down.
        """
        trail_pct = self.settings.trailing_stop_percentage

        if symbol not in self.trailing_stops:
            # Initialize trailing stop
            self.trailing_stops[symbol] = current_price * (1 - trail_pct)
        else:
            # Update only if new stop is higher
            new_stop = current_price * (1 - trail_pct)
            if new_stop > self.trailing_stops[symbol]:
                logger.debug(f"Updating trailing stop for {symbol}: {self.trailing_stops[symbol]:.2f} -> {new_stop:.2f}")
                self.trailing_stops[symbol] = new_stop

    def check_trailing_stop(self, symbol: str, current_price: float) -> tuple[bool, Optional[str]]:
        """Check if trailing stop has been hit."""
        if symbol in self.trailing_stops:
            if current_price <= self.trailing_stops[symbol]:
                logger.info(f"Trailing stop hit for {symbol} at {current_price:.2f}")
                return True, f"Trailing stop hit at {current_price:.2f}"

        return False, None

    def check_time_stop(self, symbol: str, max_hold_hours: int = 24) -> tuple[bool, Optional[str]]:
        """Check if position has been held too long without profit."""
        if symbol in self.entry_times:
            hold_time = datetime.now() - self.entry_times[symbol]
            if hold_time > timedelta(hours=max_hold_hours):
                logger.info(f"Time stop triggered for {symbol} after {hold_time}")
                return True, f"Time limit exceeded ({hold_time})"

        return False, None

    def register_entry(self, symbol: str, entry_price: float):
        """Register a new position entry."""
        self.entry_times[symbol] = datetime.now()
        self.trailing_stops[symbol] = entry_price * (1 - self.settings.trailing_stop_percentage)
        logger.info(f"Registered entry for {symbol} at {entry_price:.2f}")

    def clear_position(self, symbol: str):
        """Clear tracking for a closed position."""
        if symbol in self.trailing_stops:
            del self.trailing_stops[symbol]
        if symbol in self.entry_times:
            del self.entry_times[symbol]
        logger.info(f"Cleared position tracking for {symbol}")
