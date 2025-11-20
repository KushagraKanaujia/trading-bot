"""Tests for portfolio risk management."""

import pytest
import numpy as np
from src.risk.portfolio_risk import PortfolioRisk


@pytest.fixture
def portfolio_risk():
    """Create portfolio risk manager."""
    return PortfolioRisk()


def test_exposure_limit_check(portfolio_risk):
    """Test portfolio exposure limit checking."""
    # 10% of account is within limit
    result = portfolio_risk.check_exposure_limit(
        new_position_value=10000,
        account_value=100000
    )
    assert result is True

    # 60% of account exceeds limit
    result = portfolio_risk.check_exposure_limit(
        new_position_value=60000,
        account_value=100000
    )
    assert result is False


def test_calculate_correlation(portfolio_risk):
    """Test correlation calculation."""
    prices1 = [100, 101, 102, 103, 104, 105]
    prices2 = [200, 202, 204, 206, 208, 210]  # Highly correlated

    corr = portfolio_risk._calculate_correlation(prices1, prices2)

    assert -1 <= corr <= 1
    assert corr > 0.9  # Should be highly correlated


def test_calculate_correlation_inverse(portfolio_risk):
    """Test correlation with inverse relationship."""
    prices1 = [100, 101, 102, 103, 104, 105]
    prices2 = [210, 208, 206, 204, 202, 200]  # Inverse correlation

    corr = portfolio_risk._calculate_correlation(prices1, prices2)

    assert -1 <= corr <= 1
    assert corr < -0.9  # Should be negatively correlated


def test_calculate_correlation_insufficient_data(portfolio_risk):
    """Test correlation with insufficient data."""
    prices1 = [100, 101]
    prices2 = [200, 202]

    corr = portfolio_risk._calculate_correlation(prices1, prices2)

    assert corr == 0.0  # Should return 0 for insufficient data


def test_calculate_correlation_empty(portfolio_risk):
    """Test correlation with empty data."""
    prices1 = []
    prices2 = []

    corr = portfolio_risk._calculate_correlation(prices1, prices2)

    assert corr == 0.0


def test_var_calculation(portfolio_risk, db_session, sample_price_history):
    """Test Value at Risk calculation."""
    var = portfolio_risk.calculate_var(db_session, confidence=0.95)

    assert var >= 0  # VaR should be positive (magnitude)


def test_portfolio_beta_calculation(portfolio_risk, db_session, sample_price_history):
    """Test portfolio beta calculation."""
    # Add SPY price history for benchmark
    from src.models import PriceHistory
    from datetime import datetime, timedelta

    base_date = datetime.now() - timedelta(days=90)
    for i in range(90):
        spy_price = PriceHistory(
            timestamp=base_date + timedelta(days=i),
            symbol="SPY",
            open=400.0 + i * 0.3,
            high=405.0 + i * 0.3,
            low=398.0 + i * 0.3,
            close=402.0 + i * 0.3,
            volume=10000000
        )
        db_session.add(spy_price)
    db_session.commit()

    beta = portfolio_risk.calculate_portfolio_beta(db_session, benchmark_symbol="SPY")

    # Beta should be a reasonable number
    assert -5 <= beta <= 5


def test_check_correlation_limit_no_positions(portfolio_risk, db_session):
    """Test correlation check with no existing positions."""
    result = portfolio_risk.check_correlation_limit(db_session, "AAPL")

    assert result is True  # Should pass with no existing positions


def test_check_exposure_limit_edge_cases(portfolio_risk):
    """Test exposure limit edge cases."""
    # Exactly at limit
    result = portfolio_risk.check_exposure_limit(
        new_position_value=50000,
        account_value=100000
    )
    assert result is True

    # Just over limit
    result = portfolio_risk.check_exposure_limit(
        new_position_value=50001,
        account_value=100000
    )
    assert result is False

    # Zero position
    result = portfolio_risk.check_exposure_limit(
        new_position_value=0,
        account_value=100000
    )
    assert result is True
