from sqlalchemy import Column, Integer, DateTime, Float

from model.entity.base import Base

class DataOpenMeteo(Base):
    __tablename__ = 'data_open_meteo'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ds = Column(DateTime, unique=True)
    y = Column(Float)
    relative_humidity_2m = Column(Float)


