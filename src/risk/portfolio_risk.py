"""Portfolio-level risk management."""

import logging
import numpy as np
from typing import List, Dict
from sqlalchemy.orm import Session

from src.config import get_settings
from src.models import Position, PriceHistory

logger = logging.getLogger(__name__)


class PortfolioRisk:
    """Portfolio-level risk analysis and management."""

    def __init__(self):
        self.settings = get_settings()

    def check_exposure_limit(self, new_position_value: float, account_value: float) -> bool:
        """
        Check if adding a new position would exceed exposure limits.

        Args:
            new_position_value: Value of proposed new position
            account_value: Total account value

        Returns:
            True if within limits, False otherwise
        """
        # This would need to query current positions
        # For now, simple check
        exposure_ratio = new_position_value / account_value
        return exposure_ratio <= self.settings.max_portfolio_exposure

    def check_correlation_limit(self, session: Session, new_symbol: str) -> bool:
        """
        Check if new position would create excessive correlation.

        Args:
            session: Database session
            new_symbol: Symbol of proposed position

        Returns:
            True if correlation is acceptable, False otherwise
        """
        # Get current positions
        positions = session.query(Position).filter(Position.quantity > 0).all()

        if not positions:
            return True  # No correlation issues if no positions

        # Get existing symbols
        existing_symbols = [p.symbol for p in positions]

        # Calculate correlations
        correlations = self._calculate_correlations(session, existing_symbols, new_symbol)

        # Check if any correlation exceeds limit
        for symbol, corr in correlations.items():
            if abs(corr) > self.settings.max_correlation:
                logger.warning(f"High correlation detected: {new_symbol} vs {symbol} = {corr:.2f}")
                return False

        return True

    def _calculate_correlations(
        self,
        session: Session,
        existing_symbols: List[str],
        new_symbol: str
    ) -> Dict[str, float]:
        """Calculate correlation between new symbol and existing positions."""
        correlations = {}

        # Get price history for new symbol (last 30 days)
        new_prices = self._get_price_history(session, new_symbol, days=30)

        if not new_prices:
            logger.warning(f"No price history found for {new_symbol}")
            return {}

        for symbol in existing_symbols:
            existing_prices = self._get_price_history(session, symbol, days=30)

            if not existing_prices:
                continue

            # Calculate correlation
            corr = self._calculate_correlation(new_prices, existing_prices)
            correlations[symbol] = corr

        return correlations

    def _get_price_history(self, session: Session, symbol: str, days: int = 30) -> List[float]:
        """Get closing prices for the last N days."""
        from datetime import datetime, timedelta

        cutoff = datetime.now() - timedelta(days=days)
        prices = session.query(PriceHistory.close).filter(
            PriceHistory.symbol == symbol,
            PriceHistory.timestamp >= cutoff
        ).order_by(PriceHistory.timestamp).all()

        return [p[0] for p in prices]

    def _calculate_correlation(self, prices1: List[float], prices2: List[float]) -> float:
        """Calculate Pearson correlation coefficient."""
        if not prices1 or not prices2:
            return 0.0

        # Ensure same length
        min_len = min(len(prices1), len(prices2))
        prices1 = prices1[-min_len:]
        prices2 = prices2[-min_len:]

        if min_len < 5:  # Need at least 5 data points
            return 0.0

        # Calculate returns
        returns1 = np.diff(prices1) / prices1[:-1]
        returns2 = np.diff(prices2) / prices2[:-1]

        # Calculate correlation
        if len(returns1) > 0 and len(returns2) > 0:
            correlation = np.corrcoef(returns1, returns2)[0, 1]
            return correlation if not np.isnan(correlation) else 0.0

        return 0.0

    def calculate_var(self, session: Session, confidence: float = 0.95) -> float:
        """
        Calculate Value at Risk (VaR) for the portfolio.

        Args:
            session: Database session
            confidence: Confidence level (default 95%)

        Returns:
            VaR as a positive number (potential loss)
        """
        positions = session.query(Position).filter(Position.quantity > 0).all()

        if not positions:
            return 0.0

        portfolio_returns = []

        for position in positions:
            prices = self._get_price_history(session, position.symbol, days=30)
            if len(prices) > 1:
                returns = np.diff(prices) / prices[:-1]
                position_value = position.quantity * position.current_price if position.current_price else 0
                weighted_returns = returns * position_value
                portfolio_returns.extend(weighted_returns.tolist())

        if not portfolio_returns:
            return 0.0

        # Calculate VaR using historical method
        var = np.percentile(portfolio_returns, (1 - confidence) * 100)

        logger.info(f"Portfolio VaR ({confidence:.0%}): {abs(var):.2f}")
        return abs(var)

    def calculate_portfolio_beta(self, session: Session, benchmark_symbol: str = "SPY") -> float:
        """
        Calculate portfolio beta relative to benchmark.

        Args:
            session: Database session
            benchmark_symbol: Benchmark symbol (default SPY)

        Returns:
            Portfolio beta
        """
        positions = session.query(Position).filter(Position.quantity > 0).all()

        if not positions:
            return 0.0

        # Get benchmark returns
        benchmark_prices = self._get_price_history(session, benchmark_symbol, days=90)
        if len(benchmark_prices) < 2:
            return 1.0  # Default to 1.0 if no benchmark data

        benchmark_returns = np.diff(benchmark_prices) / benchmark_prices[:-1]

        portfolio_betas = []
        total_value = sum(p.market_value for p in positions)

        for position in positions:
            prices = self._get_price_history(session, position.symbol, days=90)
            if len(prices) > 1:
                returns = np.diff(prices) / prices[:-1]

                # Align lengths
                min_len = min(len(returns), len(benchmark_returns))
                returns = returns[-min_len:]
                bench_returns = benchmark_returns[-min_len:]

                # Calculate beta
                covariance = np.cov(returns, bench_returns)[0, 1]
                benchmark_variance = np.var(bench_returns)

                if benchmark_variance > 0:
                    beta = covariance / benchmark_variance
                    weight = position.market_value / total_value
                    portfolio_betas.append(beta * weight)

        portfolio_beta = sum(portfolio_betas) if portfolio_betas else 1.0
        logger.info(f"Portfolio beta: {portfolio_beta:.2f}")

        return portfolio_beta
