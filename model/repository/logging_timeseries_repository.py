from sqlalchemy import insert, select, func
from sqlalchemy.orm import Session

from model.entity.logging_timeseries import LoggingTimeseries
from model.repository.BaseRepository import BaseRepository

class LoggingTimeseriesRepository(BaseRepository):

    def __init__(self, session: Session):
        super().__init__(session, LoggingTimeseries)

    def insert_from_dataframe(self, df):
        """Version optimisée avec SQLAlchemy Core"""
        data = [
            {
                "ds": row['ds'],
                "relative_humidity_2m": row['relative_humidity_2m'],  # Nom exact de la colonne
            }
            for _, row in df.iterrows()
        ]

        stmt = insert(LoggingTimeseries.__table__)

        self.session.execute(stmt, data)
        self.session.commit()

    def get_best_model(self)->LoggingTimeseries:
        """Retourne le LoggingTimeseries avec le score le plus bas,
        en excluant les model_id vides ou contenant 'notebook'."""
        subquery = (
            select(func.min(LoggingTimeseries.score))
            .where(
                LoggingTimeseries.model_id.isnot(None),
                LoggingTimeseries.model_id != "",
                LoggingTimeseries.model_id.notlike("%notebook%")
            )
            .scalar_subquery()
        )
        stmt = (
            select(LoggingTimeseries)
            .where(
                LoggingTimeseries.score == subquery,
                LoggingTimeseries.model_id.isnot(None),
                LoggingTimeseries.model_id != "",
                LoggingTimeseries.model_id.notlike("%notebook%")
            )
            .limit(1)
        )
        result = self.session.execute(stmt).scalar_one_or_none()
        return result


