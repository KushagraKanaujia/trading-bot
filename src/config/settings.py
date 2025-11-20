"""Application settings and configuration."""

import os
from typing import Optional

try:
    from pydantic_settings import BaseSettings
    from pydantic import Field, field_validator
    PYDANTIC_V2 = True
except ImportError:
    from pydantic import BaseSettings, Field, validator
    PYDANTIC_V2 = False


class Settings(BaseSettings):
    """Application configuration settings."""

    # Alpaca API Configuration
    apca_api_base_url: str = "https://paper-api.alpaca.markets"
    apca_api_key_id: str = "your_api_key_here"
    apca_api_secret_key: str = "your_api_secret_here"

    # Database Configuration
    database_url: str = "sqlite:///trading_bot.db"
    redis_url: str = "redis://localhost:6379/0"

    # OpenAI Configuration
    openai_api_key: Optional[str] = None

    # Application Configuration
    flask_env: str = "development"
    secret_key: str = "change_this_secret_key"
    jwt_secret_key: str = "change_this_jwt_secret"
    debug: bool = False

    # Risk Management Configuration
    max_position_size: float = 0.02
    max_portfolio_exposure: float = 0.5
    daily_loss_limit: float = 0.05
    max_drawdown_limit: float = 0.15
    max_correlation: float = 0.7

    # Trading Configuration
    default_trade_amount: int = 1
    buy_threshold: float = -2.0
    sell_threshold: float = 2.5

    # Stop Loss Configuration
    stop_loss_percentage: float = 0.02
    take_profit_percentage: float = 0.05
    trailing_stop_percentage: float = 0.03

    # Backtesting Configuration
    backtest_start_date: str = "2022-01-01"
    backtest_end_date: str = "2024-01-01"
    backtest_initial_capital: float = 100000.0

    # ML Configuration
    ml_retrain_days: int = 7
    ml_confidence_threshold: float = 0.7

    class Config:
        """Pydantic config."""
        env_file = ".env"
        case_sensitive = False
        env_file_encoding = 'utf-8'
        protected_namespaces = ()  # Disable protected namespace warnings


# Singleton instance
_settings: Optional[Settings] = None


def get_settings() -> Settings:
    """Get or create settings instance."""
    global _settings
    if _settings is None:
        _settings = Settings()
    return _settings
