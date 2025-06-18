import pandas as pd
from sqlalchemy import insert
from sqlalchemy.orm import Session

from model.entity.data_predict_timeseries import DataPredictTimeseries
from model.repository.BaseRepository import BaseRepository

class DataPredictTimeseriesRepository(BaseRepository):

    def __init__(self, session: Session):
        super().__init__(session, DataPredictTimeseries)

    def insert_from_dataframe(self, df: pd.DataFrame, model_id: str):
        """Version optimisée avec SQLAlchemy Core"""
        data = [
            {
                "ds": row['ds'],
                "y": row['y'],
                "model_id": model_id,
            }
            for _, row in df.iterrows()
        ]

        stmt = insert(DataPredictTimeseries.__table__)

        self.session.execute(stmt, data)
        self.session.commit()