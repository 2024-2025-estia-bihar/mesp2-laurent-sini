from sqlalchemy import Column, Integer, DateTime, Float, String, JSON, Index

from model.entity.base import Base

class TimeSeriesPrediction(Base):
    __tablename__ = 'time_series_prediction'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime)  # Date/heure de la prédiction
    model_type = Column(String)  # 'ARIMA', 'SARIMA', 'Prophet', etc.

    # Autres paramètres
    model_params = Column(JSON)
    prediction_horizon = Column(Integer)

    __table_args__ = (
        Index('idx_model_type', 'model_type'),
        Index('idx_timestamp', 'timestamp')
    )
