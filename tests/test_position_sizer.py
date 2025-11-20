"""Tests for position sizing."""

import pytest
from src.risk.position_sizer import PositionSizer, KellyCriterion


def test_kelly_criterion_calculation():
    """Test Kelly Criterion calculation."""
    kelly = KellyCriterion()

    # Win rate 60%, W/L ratio 1.5
    result = kelly.calculate(win_rate=0.60, avg_win=150, avg_loss=100, fraction=0.5)

    assert result > 0
    assert result <= 0.20  # Should be capped at 20%


def test_kelly_criterion_invalid_inputs():
    """Test Kelly Criterion with invalid inputs."""
    kelly = KellyCriterion()

    # Zero loss should return default
    result = kelly.calculate(win_rate=0.60, avg_win=150, avg_loss=0, fraction=0.5)
    assert result == 0.02  # Default


def test_position_sizer_fixed_percentage():
    """Test fixed percentage position sizing."""
    sizer = PositionSizer()

    size = sizer.calculate_size(
        price=100.0,
        account_value=10000.0,
        max_risk_per_trade=0.02
    )

    assert size == 2  # (10000 * 0.02) / 100 = 2 shares


def test_position_sizer_with_volatility():
    """Test volatility-adjusted position sizing."""
    sizer = PositionSizer()

    size = sizer.calculate_size(
        price=100.0,
        account_value=10000.0,
        max_risk_per_trade=0.02,
        volatility=5.0  # High volatility
    )

    # Should return at least 1 share
    assert size >= 1
    assert isinstance(size, int)


def test_position_sizer_with_kelly():
    """Test position sizing with Kelly Criterion."""
    sizer = PositionSizer()

    size = sizer.calculate_size(
        price=100.0,
        account_value=10000.0,
        max_risk_per_trade=0.02,
        volatility=5.0,
        win_rate=0.55,
        avg_win=150,
        avg_loss=100
    )

    # Should use most conservative method
    assert size >= 1
    assert isinstance(size, int)


def test_position_sizer_minimum_size():
    """Test that position sizer returns at least 1 share."""
    sizer = PositionSizer()

    size = sizer.calculate_size(
        price=10000.0,  # Very high price
        account_value=10000.0,
        max_risk_per_trade=0.001  # Very low risk
    )

    assert size >= 1  # Should never return 0


def test_kelly_criterion_high_win_rate():
    """Test Kelly with high win rate."""
    kelly = KellyCriterion()

    result = kelly.calculate(win_rate=0.80, avg_win=200, avg_loss=100, fraction=0.5)

    assert result > 0
    assert result <= 0.20  # Should be capped


def test_kelly_criterion_low_win_rate():
    """Test Kelly with low win rate."""
    kelly = KellyCriterion()

    result = kelly.calculate(win_rate=0.30, avg_win=200, avg_loss=100, fraction=0.5)

    # Low win rate should result in low or zero allocation
    assert result >= 0
    assert result < 0.10
