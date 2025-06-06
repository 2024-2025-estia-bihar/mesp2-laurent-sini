from sqlalchemy import Column, Integer, DateTime, Float

from model.entity.base import Base

class ExogOpenMeteo(Base):
    __tablename__ = 'exog_open_meteo'

    id = Column(Integer, primary_key=True, autoincrement=True)
    ds = Column(DateTime, unique=True)
    relative_humidity_2m = Column(Float)
