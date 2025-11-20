"""Tests for database models."""

import pytest
from datetime import datetime

from src.models import Trade, Position, PriceHistory, PerformanceMetrics
from src.models.trade import Side, TradeStatus


def test_trade_creation(sample_trade):
    """Test trade model creation."""
    assert sample_trade.symbol == "AAPL"
    assert sample_trade.side == Side.BUY
    assert sample_trade.quantity == 10
    assert sample_trade.price == 175.0
    assert sample_trade.status == TradeStatus.FILLED


def test_trade_total_value(sample_trade):
    """Test trade total value calculation."""
    expected = (10 * 175.0) + 1.0  # quantity * price + commission
    assert sample_trade.total_value == expected


def test_position_creation(sample_position):
    """Test position model creation."""
    assert sample_position.symbol == "AAPL"
    assert sample_position.quantity == 10
    assert sample_position.avg_cost == 175.0
    assert sample_position.current_price == 180.0


def test_position_market_value(sample_position):
    """Test position market value calculation."""
    expected = 10 * 180.0  # quantity * current_price
    assert sample_position.market_value == expected


def test_position_total_pnl(sample_position):
    """Test position total P&L calculation."""
    sample_position.realized_pnl = 100.0
    sample_position.unrealized_pnl = 50.0
    assert sample_position.total_pnl == 150.0


def test_price_history_creation(sample_price_history):
    """Test price history model creation."""
    assert len(sample_price_history) == 30
    first_price = sample_price_history[0]
    assert first_price.symbol == "AAPL"
    assert first_price.open > 0
    assert first_price.high > first_price.low


def test_price_history_ohlc(sample_price_history):
    """Test price history OHLC property."""
    price = sample_price_history[0]
    ohlc = price.ohlc
    assert "open" in ohlc
    assert "high" in ohlc
    assert "low" in ohlc
    assert "close" in ohlc
    assert "volume" in ohlc


def test_performance_metrics_creation(sample_performance_metrics):
    """Test performance metrics model creation."""
    assert sample_performance_metrics.strategy_name == "test_strategy"
    assert sample_performance_metrics.total_pnl == 1000.0
    assert sample_performance_metrics.sharpe_ratio == 1.5
    assert sample_performance_metrics.win_rate == 0.60


def test_position_query(db_session, sample_position):
    """Test querying positions."""
    positions = db_session.query(Position).filter(Position.symbol == "AAPL").all()
    assert len(positions) == 1
    assert positions[0].symbol == "AAPL"


def test_trade_query_by_status(db_session, sample_trade):
    """Test querying trades by status."""
    trades = db_session.query(Trade).filter(Trade.status == TradeStatus.FILLED).all()
    assert len(trades) >= 1
    assert all(t.status == TradeStatus.FILLED for t in trades)
