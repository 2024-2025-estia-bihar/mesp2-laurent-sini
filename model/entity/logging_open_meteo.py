from sqlalchemy import Column, Integer, DateTime, String, JSON, Index, Float

from model.entity.base import Base

class TunerLoggingOpenMeteo(Base):
    __tablename__ = 'logging_tuner_open_meteo'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime)  # Date/heure de la prédiction
    model = Column(String)  # 'ARIMA', 'SARIMA', 'Prophet', etc.
    model_id = Column(String, default=None)
    score = Column(Float, nullable=True)
    params = Column(JSON)
    results = Column(JSON)

    def __str__(self):
        return (f"Timestamp: {self.timestamp}\n"
                f"Model: {self.model}\n"
                f"Params: {self.params}\n"
                f"Score: {self.score}\n"
                f"Results: {self.results}")
