"""Main risk management orchestration."""

import logging
from typing import Optional, Dict, Any
from datetime import datetime, timedelta

from src.config import get_settings
from src.models import get_session, Trade, Position, PerformanceMetrics
from .position_sizer import PositionSizer
from .stop_loss import StopLossManager
from .portfolio_risk import PortfolioRisk

logger = logging.getLogger(__name__)


class RiskManager:
    """Main risk manager that orchestrates all risk controls."""

    def __init__(self):
        self.settings = get_settings()
        self.position_sizer = PositionSizer()
        self.stop_loss_manager = StopLossManager()
        self.portfolio_risk = PortfolioRisk()

    def can_open_position(
        self,
        symbol: str,
        side: str,
        proposed_quantity: float,
        price: float,
        account_value: float
    ) -> tuple[bool, Optional[str]]:
        """
        Check if a position can be opened based on risk rules.

        Returns:
            tuple: (can_trade, reason)
        """
        # Check daily loss limit
        if not self._check_daily_loss_limit():
            return False, "Daily loss limit exceeded"

        # Check max drawdown
        if not self._check_max_drawdown():
            return False, "Maximum drawdown limit exceeded"

        # Check position size limit
        position_value = proposed_quantity * price
        if position_value > account_value * self.settings.max_position_size:
            return False, f"Position size exceeds max limit of {self.settings.max_position_size * 100}%"

        # Check portfolio exposure
        if not self.portfolio_risk.check_exposure_limit(position_value, account_value):
            return False, f"Portfolio exposure limit of {self.settings.max_portfolio_exposure * 100}% exceeded"

        # Check correlation limits
        with get_session() as session:
            if not self.portfolio_risk.check_correlation_limit(session, symbol):
                return False, f"Correlation limit with existing positions exceeded"

        logger.info(f"Risk check passed for {symbol} {side} {proposed_quantity}@{price}")
        return True, None

    def calculate_position_size(
        self,
        symbol: str,
        price: float,
        account_value: float,
        volatility: Optional[float] = None,
        win_rate: Optional[float] = None,
        avg_win: Optional[float] = None,
        avg_loss: Optional[float] = None
    ) -> int:
        """
        Calculate optimal position size based on risk parameters.

        Args:
            symbol: Stock symbol
            price: Current price
            account_value: Total account value
            volatility: Optional ATR or volatility measure
            win_rate: Historical win rate for Kelly Criterion
            avg_win: Average win amount
            avg_loss: Average loss amount

        Returns:
            Recommended position size (number of shares)
        """
        return self.position_sizer.calculate_size(
            price=price,
            account_value=account_value,
            max_risk_per_trade=self.settings.max_position_size,
            volatility=volatility,
            win_rate=win_rate,
            avg_win=avg_win,
            avg_loss=avg_loss
        )

    def should_exit_position(
        self,
        symbol: str,
        entry_price: float,
        current_price: float,
        quantity: float,
        side: str
    ) -> tuple[bool, Optional[str]]:
        """
        Check if a position should be exited based on stop-loss/take-profit.

        Returns:
            tuple: (should_exit, reason)
        """
        return self.stop_loss_manager.should_exit(
            entry_price=entry_price,
            current_price=current_price,
            quantity=quantity,
            side=side
        )

    def update_trailing_stops(self, symbol: str, current_price: float):
        """Update trailing stop for a position."""
        self.stop_loss_manager.update_trailing_stop(symbol, current_price)

    def _check_daily_loss_limit(self) -> bool:
        """Check if daily loss limit has been exceeded."""
        with get_session() as session:
            today = datetime.now().date()
            metrics = session.query(PerformanceMetrics).filter(
                PerformanceMetrics.date == today
            ).first()

            if metrics and metrics.total_pnl < 0:
                loss_percentage = abs(metrics.total_pnl) / metrics.portfolio_value
                if loss_percentage > self.settings.daily_loss_limit:
                    logger.warning(f"Daily loss limit exceeded: {loss_percentage:.2%}")
                    return False

        return True

    def _check_max_drawdown(self) -> bool:
        """Check if maximum drawdown has been exceeded."""
        with get_session() as session:
            # Get performance metrics from last 30 days
            cutoff_date = datetime.now().date() - timedelta(days=30)
            metrics = session.query(PerformanceMetrics).filter(
                PerformanceMetrics.date >= cutoff_date
            ).order_by(PerformanceMetrics.date.desc()).all()

            if not metrics:
                return True

            # Find peak and current value
            peak_value = max(m.portfolio_value for m in metrics if m.portfolio_value)
            current_value = metrics[0].portfolio_value if metrics[0].portfolio_value else peak_value

            if peak_value > 0:
                drawdown = (peak_value - current_value) / peak_value
                if drawdown > self.settings.max_drawdown_limit:
                    logger.warning(f"Max drawdown exceeded: {drawdown:.2%}")
                    return False

        return True

    def get_risk_summary(self) -> Dict[str, Any]:
        """Get current risk status summary."""
        with get_session() as session:
            today = datetime.now().date()
            metrics = session.query(PerformanceMetrics).filter(
                PerformanceMetrics.date == today
            ).first()

            portfolio_value = metrics.portfolio_value if metrics else 0
            daily_pnl = metrics.total_pnl if metrics else 0
            current_drawdown = metrics.current_drawdown if metrics else 0
            exposure = metrics.exposure if metrics else 0

            return {
                'portfolio_value': portfolio_value,
                'daily_pnl': daily_pnl,
                'daily_pnl_pct': (daily_pnl / portfolio_value * 100) if portfolio_value else 0,
                'current_drawdown': current_drawdown,
                'current_drawdown_pct': (current_drawdown / portfolio_value * 100) if portfolio_value else 0,
                'exposure': exposure,
                'exposure_pct': (exposure / portfolio_value * 100) if portfolio_value else 0,
                'daily_loss_limit': self.settings.daily_loss_limit * 100,
                'max_drawdown_limit': self.settings.max_drawdown_limit * 100,
                'max_exposure_limit': self.settings.max_portfolio_exposure * 100,
                'can_trade': self._check_daily_loss_limit() and self._check_max_drawdown()
            }
