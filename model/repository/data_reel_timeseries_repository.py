from sqlalchemy import insert
from sqlalchemy.orm import Session

from model.entity.data_reel_timeseries import DataReelTimeseries
from model.repository.BaseRepository import BaseRepository

class DataReelTimeseriesRepository(BaseRepository):

    def __init__(self, session: Session):
        super().__init__(session, DataReelTimeseries)

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

        stmt = insert(DataReelTimeseries.__table__)

        self.session.execute(stmt, data)
        self.session.commit()