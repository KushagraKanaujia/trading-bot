"""Performance metrics model for tracking strategy performance."""

from sqlalchemy import Column, Integer, String, Float, DateTime, Date
from sqlalchemy.sql import func

from .base import Base


class PerformanceMetrics(Base):
    """Performance metrics model for tracking daily/strategy performance."""

    __tablename__ = "performance_metrics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(Date, nullable=False, index=True)
    strategy_name = Column(String(50), nullable=True, index=True)

    # P&L Metrics
    total_pnl = Column(Float, default=0.0)
    realized_pnl = Column(Float, default=0.0)
    unrealized_pnl = Column(Float, default=0.0)

    # Performance Ratios
    sharpe_ratio = Column(Float, nullable=True)
    sortino_ratio = Column(Float, nullable=True)
    calmar_ratio = Column(Float, nullable=True)

    # Drawdown Metrics
    max_drawdown = Column(Float, nullable=True)
    current_drawdown = Column(Float, nullable=True)

    # Win/Loss Statistics
    win_rate = Column(Float, nullable=True)
    profit_factor = Column(Float, nullable=True)
    avg_win = Column(Float, nullable=True)
    avg_loss = Column(Float, nullable=True)

    # Trading Statistics
    total_trades = Column(Integer, default=0)
    winning_trades = Column(Integer, default=0)
    losing_trades = Column(Integer, default=0)

    # Portfolio Metrics
    portfolio_value = Column(Float, nullable=True)
    cash_balance = Column(Float, nullable=True)
    exposure = Column(Float, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<PerformanceMetrics {self.date} {self.strategy_name} pnl={self.total_pnl}>"
