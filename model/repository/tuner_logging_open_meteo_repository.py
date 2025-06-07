from sqlalchemy import insert
from sqlalchemy.orm import Session

from model.entity.tuner_logging_open_meteo import TunerLoggingOpenMeteo
from model.repository.BaseRepository import BaseRepository

class TunerLoggingOpenMeteoRepository(BaseRepository):

    def __init__(self, session: Session):
        super().__init__(session, TunerLoggingOpenMeteo)

    def insert_from_dataframe(self, df):
        """Version optimisée avec SQLAlchemy Core"""
        data = [
            {
                "ds": row['ds'],
                "relative_humidity_2m": row['relative_humidity_2m'],  # Nom exact de la colonne
            }
            for _, row in df.iterrows()
        ]

        stmt = insert(TunerLoggingOpenMeteo.__table__)

        self.session.execute(stmt, data)
        self.session.commit()