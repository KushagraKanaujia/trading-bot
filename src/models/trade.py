"""Trade model for storing trade history."""

from sqlalchemy import Column, Integer, String, Float, DateTime, Enum
from sqlalchemy.sql import func
import enum

from .base import Base


class Side(enum.Enum):
    """Trade side enum."""
    BUY = "buy"
    SELL = "sell"


class TradeStatus(enum.Enum):
    """Trade status enum."""
    PENDING = "pending"
    FILLED = "filled"
    CANCELLED = "cancelled"
    REJECTED = "rejected"


class Trade(Base):
    """Trade model for storing executed trades."""

    __tablename__ = "trades"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), server_default=func.now(), index=True)
    symbol = Column(String(10), nullable=False, index=True)
    side = Column(Enum(Side), nullable=False)
    quantity = Column(Float, nullable=False)
    price = Column(Float, nullable=False)
    commission = Column(Float, default=0.0)
    status = Column(Enum(TradeStatus), default=TradeStatus.PENDING, index=True)
    strategy_name = Column(String(50), nullable=True, index=True)
    order_id = Column(String(100), nullable=True, unique=True)
    pnl = Column(Float, nullable=True)
    notes = Column(String(500), nullable=True)

    def __repr__(self):
        return f"<Trade {self.symbol} {self.side.value} {self.quantity}@{self.price}>"

    @property
    def total_value(self) -> float:
        """Calculate total value of trade."""
        return self.quantity * self.price + self.commission
