from sqlalchemy import Column, Integer, DateTime, Float, func, String, ForeignKey

from model.entity.base import Base

class DataPredictTimeseries(Base):
    __tablename__ = 'data_predict_timeseries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ds = Column(DateTime)
    y = Column(Float)
    confidence_score = Column(Float)
    relative_humidity_2m = Column(Float)
    model_ref = Column(Integer, ForeignKey('logging_timeseries.id'))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
