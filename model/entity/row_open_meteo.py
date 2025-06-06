from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, Float, UniqueConstraint

Base = declarative_base()

class RowOpenMeteo(Base):
    __tablename__ = 'row_open_meteo'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, unique=True)
    temperature_2m = Column(Float)
    relative_humidity_2m = Column(Float)
