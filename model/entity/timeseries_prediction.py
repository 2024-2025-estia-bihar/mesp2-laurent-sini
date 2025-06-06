from sqlalchemy import Column, Integer, DateTime, Float, String, JSON, Index

from model.entity.base import Base

class TimeSeriesPrediction(Base):
    __tablename__ = 'time_series_prediction'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime)  # Date/heure de la prédiction
    model_type = Column(String)  # 'ARIMA', 'SARIMA', 'Prophet', etc.

    # Paramètres du modèle
    order_p = Column(Integer)
    order_d = Column(Integer)
    order_q = Column(Integer)
    seasonal_p = Column(Integer, nullable=True)
    seasonal_d = Column(Integer, nullable=True)
    seasonal_q = Column(Integer, nullable=True)
    seasonal_m = Column(Integer, nullable=True)
    trend = Column(String)

    # Métriques d'évaluation
    aic = Column(Float, nullable=True)
    mae = Column(Float)
    rmse = Column(Float)
    r2 = Column(Float, nullable=True)
    mape = Column(Float, nullable=True)

    # Autres paramètres
    model_params = Column(JSON)
    prediction_horizon = Column(Integer)

    __table_args__ = (
        Index('idx_model_type', 'model_type'),
        Index('idx_timestamp', 'timestamp')
    )
