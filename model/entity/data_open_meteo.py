from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, Float

Base = declarative_base()

class DataOpenMeteo(Base):
    __tablename__ = 'data_open_meteo'

    id = Column(Integer, primary_key=True, autoincrement=True)
    timestamp = Column(DateTime, unique=True)
    temperature_2m = Column(Float)


