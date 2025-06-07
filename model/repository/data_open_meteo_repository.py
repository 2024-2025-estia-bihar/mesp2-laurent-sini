from sqlalchemy import insert, update
from sqlalchemy.orm import Session

from model.entity.data_open_meteo import DataOpenMeteo
from model.repository.BaseRepository import BaseRepository

class DataOpenMeteoRepository(BaseRepository):

    def __init__(self, session: Session):
        super().__init__(session, DataOpenMeteo)

    def insert_from_dataframe(self, df):
        """Version optimisée avec SQLAlchemy Core"""
        data = [
            {
                "ds": row['ds'],
                "y": row['y'],
                "relative_humidity_2m": row['relative_humidity_2m'],
            }
            for _, row in df.iterrows()
        ]

        stmt = insert(DataOpenMeteo.__table__)

        self.session.execute(stmt, data)
        self.session.commit()