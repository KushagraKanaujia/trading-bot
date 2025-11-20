"""Position model for tracking current holdings."""

from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func

from .base import Base


class Position(Base):
    """Position model for tracking current holdings."""

    __tablename__ = "positions"

    id = Column(Integer, primary_key=True, index=True)
    symbol = Column(String(10), nullable=False, unique=True, index=True)
    quantity = Column(Float, nullable=False)
    avg_cost = Column(Float, nullable=False)
    current_price = Column(Float, nullable=True)
    unrealized_pnl = Column(Float, nullable=True)
    realized_pnl = Column(Float, default=0.0)
    last_updated = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    def __repr__(self):
        return f"<Position {self.symbol} qty={self.quantity} cost={self.avg_cost}>"

    @property
    def market_value(self) -> float:
        """Calculate current market value."""
        if self.current_price:
            return self.quantity * self.current_price
        return self.quantity * self.avg_cost

    @property
    def total_pnl(self) -> float:
        """Calculate total P&L (realized + unrealized)."""
        unrealized = self.unrealized_pnl or 0.0
        return self.realized_pnl + unrealized
