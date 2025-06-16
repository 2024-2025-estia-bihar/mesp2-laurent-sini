from sqlalchemy import Column, Integer, DateTime, Float

from model.entity.base import Base

class DataReelTimeseries(Base):
    __tablename__ = 'data_reel_timeseries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    time = Column(DateTime, unique=True)
    temperature_2m = Column(Float)
    relative_humidity_2m = Column(Float)
