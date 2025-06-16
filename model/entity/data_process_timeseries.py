from sqlalchemy import Column, Integer, DateTime, Float

from model.entity.base import Base

class DataProcessTimeseries(Base):
    __tablename__ = 'data_process_timeseries'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ds = Column(DateTime, unique=True)
    y = Column(Float)
    relative_humidity_2m = Column(Float)


