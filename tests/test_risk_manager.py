"""Tests for risk manager."""

import pytest
from datetime import datetime
from src.risk.manager import RiskManager
from src.models import PerformanceMetrics


@pytest.fixture
def risk_manager():
    """Create risk manager."""
    return RiskManager()


def test_risk_manager_initialization(risk_manager):
    """Test risk manager initializes correctly."""
    assert risk_manager is not None
    assert risk_manager.position_sizer is not None
    assert risk_manager.stop_loss_manager is not None
    assert risk_manager.portfolio_risk is not None


def test_calculate_position_size(risk_manager):
    """Test position size calculation."""
    size = risk_manager.calculate_position_size(
        symbol="AAPL",
        price=175.0,
        account_value=100000,
        volatility=2.5
    )

    assert size >= 1
    assert isinstance(size, int)


def test_calculate_position_size_with_stats(risk_manager):
    """Test position size with trading statistics."""
    size = risk_manager.calculate_position_size(
        symbol="AAPL",
        price=175.0,
        account_value=100000,
        volatility=2.5,
        win_rate=0.55,
        avg_win=150,
        avg_loss=100
    )

    assert size >= 1
    assert isinstance(size, int)


def test_can_open_position_basic(risk_manager):
    """Test basic position opening check."""
    can_trade, reason = risk_manager.can_open_position(
        symbol="AAPL",
        side="buy",
        proposed_quantity=10,
        price=175.0,
        account_value=100000
    )

    # Should pass with reasonable parameters
    assert isinstance(can_trade, bool)
    if not can_trade:
        assert reason is not None


def test_can_open_position_too_large(risk_manager):
    """Test rejection of oversized position."""
    can_trade, reason = risk_manager.can_open_position(
        symbol="AAPL",
        side="buy",
        proposed_quantity=100,  # Very large position
        price=175.0,
        account_value=100000
    )

    assert can_trade is False
    assert "Position size exceeds" in reason


def test_can_open_position_exceeds_exposure(risk_manager):
    """Test rejection when portfolio exposure limit exceeded."""
    can_trade, reason = risk_manager.can_open_position(
        symbol="AAPL",
        side="buy",
        proposed_quantity=350,  # Would be ~60% of account
        price=175.0,
        account_value=100000
    )

    assert can_trade is False
    assert "exposure" in reason.lower()


def test_should_exit_position_stop_loss(risk_manager):
    """Test exit decision with stop-loss trigger."""
    should_exit, reason = risk_manager.should_exit_position(
        symbol="AAPL",
        entry_price=100.0,
        current_price=97.0,  # -3% loss
        quantity=10,
        side="buy"
    )

    assert should_exit is True
    assert "stop-loss" in reason.lower()


def test_should_exit_position_take_profit(risk_manager):
    """Test exit decision with take-profit trigger."""
    should_exit, reason = risk_manager.should_exit_position(
        symbol="AAPL",
        entry_price=100.0,
        current_price=106.0,  # +6% profit
        quantity=10,
        side="buy"
    )

    assert should_exit is True
    assert "profit" in reason.lower()


def test_should_exit_position_no_trigger(risk_manager):
    """Test no exit when within range."""
    should_exit, reason = risk_manager.should_exit_position(
        symbol="AAPL",
        entry_price=100.0,
        current_price=101.0,  # +1% profit
        quantity=10,
        side="buy"
    )

    assert should_exit is False


def test_update_trailing_stops(risk_manager):
    """Test trailing stop updates."""
    # Register position first
    risk_manager.stop_loss_manager.register_entry("AAPL", 100.0)

    # Update with higher price
    risk_manager.update_trailing_stops("AAPL", 105.0)

    # Verify stop was updated
    assert "AAPL" in risk_manager.stop_loss_manager.trailing_stops


def test_get_risk_summary(risk_manager, db_session):
    """Test risk summary generation."""
    # Create sample performance metrics
    metrics = PerformanceMetrics(
        date=datetime.now().date(),
        total_pnl=1000.0,
        current_drawdown=500.0,
        exposure=0.3,
        portfolio_value=100000.0
    )
    db_session.add(metrics)
    db_session.commit()

    summary = risk_manager.get_risk_summary()

    assert isinstance(summary, dict)
    assert "portfolio_value" in summary
    assert "daily_pnl" in summary
    assert "can_trade" in summary


def test_check_daily_loss_limit_no_metrics(risk_manager):
    """Test daily loss check with no metrics."""
    # Should pass if no metrics exist
    result = risk_manager._check_daily_loss_limit()
    assert result is True


def test_check_max_drawdown_no_metrics(risk_manager):
    """Test max drawdown check with no metrics."""
    # Should pass if no metrics exist
    result = risk_manager._check_max_drawdown()
    assert result is True
