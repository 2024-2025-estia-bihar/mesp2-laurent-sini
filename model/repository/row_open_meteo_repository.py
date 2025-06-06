from sqlalchemy import insert
from sqlalchemy.orm import Session

from model.entity.row_open_meteo import RowOpenMeteo
from model.repository.BaseRepository import BaseRepository

class RowOpenMeteoRepository(BaseRepository):

    def __init__(self, session: Session):
        super().__init__(session, RowOpenMeteo)

    def insert_from_dataframe(self, df):
        """Version optimisée avec SQLAlchemy Core"""
        data = [
            {
                "timestamp": row['time'],
                "temperature_2m": row['temperature_2m'],  # Nom exact de la colonne
                "relative_humidity_2m": row['relative_humidity_2m']
            }
            for _, row in df.iterrows()
        ]

        stmt = insert(RowOpenMeteo.__table__)

        self.session.execute(stmt, data)
        self.session.commit()