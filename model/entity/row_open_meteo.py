from sqlalchemy import Column, Integer, DateTime, Float, UniqueConstraint

from model.entity.base import Base

class RowOpenMeteo(Base):
    __tablename__ = 'row_open_meteo'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, unique=True)
    temperature_2m = Column(Float)
    relative_humidity_2m = Column(Float)
