"""Tests for stop-loss management."""

import pytest
from datetime import datetime, timedelta
from src.risk.stop_loss import StopLossManager
from src.config import get_settings


@pytest.fixture
def stop_manager():
    """Create a stop-loss manager."""
    return StopLossManager()


def test_stop_loss_triggered_long(stop_manager):
    """Test stop-loss trigger for long position."""
    entry_price = 100.0
    current_price = 97.5  # -2.5% loss

    should_exit, reason = stop_manager.should_exit(
        entry_price=entry_price,
        current_price=current_price,
        quantity=10,
        side="buy"
    )

    assert should_exit is True
    assert "Stop-loss" in reason


def test_take_profit_triggered_long(stop_manager):
    """Test take-profit trigger for long position."""
    entry_price = 100.0
    current_price = 106.0  # +6% profit

    should_exit, reason = stop_manager.should_exit(
        entry_price=entry_price,
        current_price=current_price,
        quantity=10,
        side="buy"
    )

    assert should_exit is True
    assert "Take-profit" in reason


def test_no_exit_within_range(stop_manager):
    """Test no exit when price within range."""
    entry_price = 100.0
    current_price = 101.0  # +1% profit

    should_exit, reason = stop_manager.should_exit(
        entry_price=entry_price,
        current_price=current_price,
        quantity=10,
        side="buy"
    )

    assert should_exit is False
    assert reason is None


def test_stop_loss_short_position(stop_manager):
    """Test stop-loss for short position."""
    entry_price = 100.0
    current_price = 103.0  # Price going up = loss for short

    should_exit, reason = stop_manager.should_exit(
        entry_price=entry_price,
        current_price=current_price,
        quantity=10,
        side="sell"
    )

    assert should_exit is True
    assert "Stop-loss" in reason


def test_take_profit_short_position(stop_manager):
    """Test take-profit for short position."""
    entry_price = 100.0
    current_price = 94.0  # Price going down = profit for short

    should_exit, reason = stop_manager.should_exit(
        entry_price=entry_price,
        current_price=current_price,
        quantity=10,
        side="sell"
    )

    assert should_exit is True
    assert "Take-profit" in reason


def test_trailing_stop_initialization(stop_manager):
    """Test trailing stop initialization."""
    symbol = "AAPL"
    entry_price = 100.0

    stop_manager.register_entry(symbol, entry_price)

    assert symbol in stop_manager.trailing_stops
    assert symbol in stop_manager.entry_times


def test_trailing_stop_update(stop_manager):
    """Test trailing stop updates as price moves."""
    symbol = "AAPL"
    entry_price = 100.0

    stop_manager.register_entry(symbol, entry_price)
    initial_stop = stop_manager.trailing_stops[symbol]

    # Price moves up
    stop_manager.update_trailing_stop(symbol, 105.0)

    # Stop should move up
    assert stop_manager.trailing_stops[symbol] > initial_stop


def test_trailing_stop_does_not_move_down(stop_manager):
    """Test that trailing stop doesn't move down."""
    symbol = "AAPL"
    entry_price = 100.0

    stop_manager.register_entry(symbol, entry_price)

    # Price moves up
    stop_manager.update_trailing_stop(symbol, 105.0)
    stop_at_105 = stop_manager.trailing_stops[symbol]

    # Price moves down
    stop_manager.update_trailing_stop(symbol, 102.0)

    # Stop should stay at higher level
    assert stop_manager.trailing_stops[symbol] == stop_at_105


def test_trailing_stop_hit(stop_manager):
    """Test trailing stop being hit."""
    symbol = "AAPL"
    entry_price = 100.0

    stop_manager.register_entry(symbol, entry_price)
    stop_manager.update_trailing_stop(symbol, 105.0)

    # Price drops below trailing stop
    should_exit, reason = stop_manager.check_trailing_stop(symbol, 100.0)

    assert should_exit is True
    assert "Trailing stop" in reason


def test_clear_position(stop_manager):
    """Test clearing position tracking."""
    symbol = "AAPL"
    entry_price = 100.0

    stop_manager.register_entry(symbol, entry_price)
    assert symbol in stop_manager.trailing_stops

    stop_manager.clear_position(symbol)

    assert symbol not in stop_manager.trailing_stops
    assert symbol not in stop_manager.entry_times
