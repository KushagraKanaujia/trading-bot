"""Price history model for time-series data."""

from sqlalchemy import Column, Integer, String, Float, DateTime, Index
from sqlalchemy.sql import func

from .base import Base


class PriceHistory(Base):
    """Price history model for time-series data."""

    __tablename__ = "price_history"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime(timezone=True), nullable=False, index=True)
    symbol = Column(String(10), nullable=False, index=True)
    open = Column(Float, nullable=False)
    high = Column(Float, nullable=False)
    low = Column(Float, nullable=False)
    close = Column(Float, nullable=False)
    volume = Column(Float, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index('ix_symbol_timestamp', 'symbol', 'timestamp'),
    )

    def __repr__(self):
        return f"<PriceHistory {self.symbol} @ {self.timestamp} close={self.close}>"

    @property
    def ohlc(self) -> dict:
        """Return OHLC as dictionary."""
        return {
            'open': self.open,
            'high': self.high,
            'low': self.low,
            'close': self.close,
            'volume': self.volume
        }
