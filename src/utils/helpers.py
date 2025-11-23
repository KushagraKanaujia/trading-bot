"""Helper utility functions."""

import numpy as np
import pandas as pd
from typing import Union


def calculate_returns(prices: Union[pd.Series, np.ndarray]) -> np.ndarray:
    """
    Calculate returns from price series.

    Args:
        prices: Price series

    Returns:
        Array of returns
    """
    if isinstance(prices, pd.Series):
        prices = prices.values

    returns = np.diff(prices) / prices[:-1]
    return returns


def calculate_sharpe_ratio(
    returns: Union[pd.Series, np.ndarray],
    risk_free_rate: float = 0.0,
    periods: int = 252
) -> float:
    """
    Calculate annualized Sharpe ratio.

    Args:
        returns: Return series
        risk_free_rate: Risk-free rate (default: 0.0)
        periods: Number of periods per year (default: 252 for daily)

    Returns:
        Sharpe ratio
    """
    if isinstance(returns, pd.Series):
        returns = returns.values

    excess_returns = returns - risk_free_rate / periods
    mean_return = np.mean(excess_returns)
    std_return = np.std(excess_returns, ddof=1)

    if std_return == 0:
        return 0.0

    sharpe = (mean_return / std_return) * np.sqrt(periods)
    return sharpe


def calculate_sortino_ratio(
    returns: Union[pd.Series, np.ndarray],
    risk_free_rate: float = 0.0,
    periods: int = 252
) -> float:
    """
    Calculate annualized Sortino ratio (downside deviation).

    Args:
        returns: Return series
        risk_free_rate: Risk-free rate
        periods: Number of periods per year

    Returns:
        Sortino ratio
    """
    if isinstance(returns, pd.Series):
        returns = returns.values

    excess_returns = returns - risk_free_rate / periods
    mean_return = np.mean(excess_returns)

    # Calculate downside deviation
    downside_returns = excess_returns[excess_returns < 0]

    if len(downside_returns) == 0:
        return 0.0

    downside_std = np.std(downside_returns, ddof=1)

    if downside_std == 0:
        return 0.0

    sortino = (mean_return / downside_std) * np.sqrt(periods)
    return sortino


def calculate_max_drawdown(equity_curve: Union[pd.Series, np.ndarray]) -> float:
    """
    Calculate maximum drawdown.

    Args:
        equity_curve: Equity curve series

    Returns:
        Maximum drawdown as positive number
    """
    if isinstance(equity_curve, pd.Series):
        equity_curve = equity_curve.values

    cummax = np.maximum.accumulate(equity_curve)
    drawdown = (equity_curve - cummax) / cummax

    max_dd = abs(np.min(drawdown))
    return max_dd
