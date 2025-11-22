"""Base strategy class for all trading strategies."""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional
import pandas as pd


class BaseStrategy(ABC):
    """Abstract base class for trading strategies."""

    def __init__(self, name: str):
        """
        Initialize strategy.

        Args:
            name: Strategy name for identification
        """
        self.name = name
        self.positions: Dict[str, float] = {}
        self.parameters: Dict[str, any] = {}

    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Generate trading signals from market data.

        Args:
            data: DataFrame with OHLCV data

        Returns:
            DataFrame with signals (1=buy, -1=sell, 0=hold)
        """
        pass

    @abstractmethod
    def calculate_indicators(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate technical indicators for the strategy.

        Args:
            data: DataFrame with OHLCV data

        Returns:
            DataFrame with added indicator columns
        """
        pass

    def set_parameters(self, **kwargs):
        """
        Set strategy parameters.

        Args:
            **kwargs: Parameter key-value pairs
        """
        self.parameters.update(kwargs)

    def get_parameters(self) -> Dict[str, any]:
        """Get current strategy parameters."""
        return self.parameters.copy()

    def reset(self):
        """Reset strategy state."""
        self.positions.clear()

    def __repr__(self):
        return f"<{self.__class__.__name__} name={self.name}>"
