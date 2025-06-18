from sqlalchemy import Column, Integer, DateTime, Float, func, String, ForeignKey

from model.entity.base import Base

class DataPredictTimeseries(Base):
    __tablename__ = 'data_predict_timeseries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ds = Column(DateTime)
    y = Column(Float)
    model_id = Column(String, nullable=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
