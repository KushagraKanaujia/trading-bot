"""ML model metadata tracking."""

from sqlalchemy import Column, Integer, String, Float, DateTime, JSON
from sqlalchemy.sql import func

from .base import Base


class MLModel(Base):
    """ML model metadata for tracking model versions and performance."""

    __tablename__ = "ml_models"

    id = Column(Integer, primary_key=True, index=True)
    model_name = Column(String(100), nullable=False, index=True)
    version = Column(String(50), nullable=False, index=True)
    model_type = Column(String(50), nullable=False)  # e.g., "neural_network", "xgboost"
    file_path = Column(String(500), nullable=False)

    # Training Metrics
    train_loss = Column(Float, nullable=True)
    val_loss = Column(Float, nullable=True)
    test_loss = Column(Float, nullable=True)
    train_accuracy = Column(Float, nullable=True)
    val_accuracy = Column(Float, nullable=True)
    test_accuracy = Column(Float, nullable=True)

    # Model Configuration
    hyperparameters = Column(JSON, nullable=True)
    feature_list = Column(JSON, nullable=True)

    # Performance Metrics
    sharpe_ratio = Column(Float, nullable=True)
    total_return = Column(Float, nullable=True)
    max_drawdown = Column(Float, nullable=True)

    # Metadata
    training_samples = Column(Integer, nullable=True)
    training_duration_seconds = Column(Float, nullable=True)
    is_active = Column(Integer, default=1)  # 1 for active, 0 for inactive
    notes = Column(String(1000), nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    trained_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<MLModel {self.model_name} v{self.version} type={self.model_type}>"
