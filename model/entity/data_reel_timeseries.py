from sqlalchemy import Column, Integer, DateTime, Float, func

from model.entity.base import Base

class DataReelTimeseries(Base):
    __tablename__ = 'data_reel'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ds = Column(DateTime, unique=True)
    y = Column(Float)
    relative_humidity_2m = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())  # Date d'insertion en base
