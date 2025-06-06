from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, DateTime, Float

Base = declarative_base()

class ExogOpenMeteo(Base):
    __tablename__ = 'exog_open_meteo'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ds = Column(DateTime, unique=True)
    relative_humidity_2m = Column(Float)
