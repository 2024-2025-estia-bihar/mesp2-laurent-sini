from sqlalchemy import insert, and_
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
                "time": row['time'],
                "temperature_2m": row['temperature_2m'],
                "relative_humidity_2m": row['relative_humidity_2m']
            }
            for _, row in df.iterrows()
        ]

        stmt = insert(DataReelTimeseries.__table__)

        self.session.execute(stmt, data)
        self.session.commit()

    def get_between_dates(self, start_date, end_date):
        """
        Récupère toutes les entrées de la table entre deux dates (incluses).
        :param start_date: datetime, date de début
        :param end_date: datetime, date de fin
        :return: Liste d'objets DataReelTimeseries
        """
        return (
            self.session.query(self.model)
            .filter(and_(
                self.model.time >= start_date,
                self.model.time <= end_date
            ))
            .all()
        )
