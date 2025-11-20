"""Pytest configuration and fixtures."""

import pytest
import os
from datetime import datetime, timedelta
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from src.models import Base, Trade, Position, PriceHistory, PerformanceMetrics
from src.models.trade import Side, TradeStatus


@pytest.fixture(scope="session")
def test_db_engine():
    """Create a test database engine."""
    # Use in-memory SQLite for testing
    engine = create_engine("sqlite:///:memory:", echo=False)
    Base.metadata.create_all(engine)
    yield engine
    engine.dispose()


@pytest.fixture
def db_session(test_db_engine):
    """Create a new database session for a test."""
    Session = sessionmaker(bind=test_db_engine)
    session = Session()
    yield session
    session.rollback()
    session.close()


@pytest.fixture
def sample_trade(db_session):
    """Create a sample trade."""
    trade = Trade(
        symbol="AAPL",
        side=Side.BUY,
        quantity=10,
        price=175.0,
        commission=1.0,
        status=TradeStatus.FILLED,
        strategy_name="test_strategy",
        order_id="test_order_123"
    )
    db_session.add(trade)
    db_session.commit()
    return trade


@pytest.fixture
def sample_position(db_session):
    """Create a sample position."""
    position = Position(
        symbol="AAPL",
        quantity=10,
        avg_cost=175.0,
        current_price=180.0,
        unrealized_pnl=50.0
    )
    db_session.add(position)
    db_session.commit()
    return position


@pytest.fixture
def sample_price_history(db_session):
    """Create sample price history."""
    prices = []
    base_date = datetime.now() - timedelta(days=30)

    for i in range(30):
        price = PriceHistory(
            timestamp=base_date + timedelta(days=i),
            symbol="AAPL",
            open=170.0 + i * 0.5,
            high=175.0 + i * 0.5,
            low=168.0 + i * 0.5,
            close=172.0 + i * 0.5,
            volume=1000000
        )
        prices.append(price)
        db_session.add(price)

    db_session.commit()
    return prices


@pytest.fixture
def sample_performance_metrics(db_session):
    """Create sample performance metrics."""
    metrics = PerformanceMetrics(
        date=datetime.now().date(),
        strategy_name="test_strategy",
        total_pnl=1000.0,
        realized_pnl=800.0,
        unrealized_pnl=200.0,
        sharpe_ratio=1.5,
        max_drawdown=-0.05,
        win_rate=0.60,
        profit_factor=2.0,
        total_trades=20,
        winning_trades=12,
        losing_trades=8,
        portfolio_value=100000.0,
        exposure=0.3
    )
    db_session.add(metrics)
    db_session.commit()
    return metrics


@pytest.fixture
def mock_settings(monkeypatch):
    """Mock settings for testing."""
    monkeypatch.setenv("APCA_API_KEY_ID", "test_key")
    monkeypatch.setenv("APCA_API_SECRET_KEY", "test_secret")
    monkeypatch.setenv("DATABASE_URL", "sqlite:///:memory:")
    monkeypatch.setenv("SECRET_KEY", "test_secret_key")
    monkeypatch.setenv("JWT_SECRET_KEY", "test_jwt_secret")
    monkeypatch.setenv("MAX_POSITION_SIZE", "0.02")
    monkeypatch.setenv("DAILY_LOSS_LIMIT", "0.05")
    monkeypatch.setenv("MAX_DRAWDOWN_LIMIT", "0.15")
