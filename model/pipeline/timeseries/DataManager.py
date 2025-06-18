import logging

import pandas as pd

from model.helpers.dataset_helper import extract_object_to_dataframe, nan_interpolation_linear
from model.pipeline.interface.DataManagerInterface import DataManagerInterface
from model.repository.data_predict_timeseries_repository import DataPredictTimeseriesRepository
from model.repository.data_process_timeseries_repository import DataProcessTimeSeriesRepository
from model.repository.data_reel_timeseries_repository import DataReelTimeseriesRepository
from model.services.database_manager import DatabaseManager


class DataManager(DataManagerInterface):

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def loadData(self) -> pd.DataFrame:
        data_reel_repository = DataReelTimeseriesRepository(self.db_manager.session)
        return extract_object_to_dataframe(data_reel_repository.getAll(), ['time', 'temperature_2m', 'relative_humidity_2m'])

    def cleanData(self, df: pd.DataFrame) -> pd.DataFrame :
        df = nan_interpolation_linear(df, 'time')
        return df

    def transformData(self, df: pd.DataFrame) -> pd.DataFrame :
        df = df.rename(columns={'time': 'ds', 'temperature_2m': 'y'})
        return df

    def saveData(self, df: pd.DataFrame) -> None:
        data_process_repository = DataProcessTimeSeriesRepository(self.db_manager.session)
        data_process_repository.delete_all()
        data_process_repository.session.commit()
        data_process_repository.insert_from_dataframe(df)

    def splitData(self, df: pd.DataFrame, train_size=0.9) -> (pd.DataFrame, pd.DataFrame):
        train_size = int(len(df) * train_size)

        train = df[:train_size]
        test = df[train_size:]
        return train, test

    def loadFutureData(self, df: pd.DataFrame) -> pd.DataFrame:
        last_date = df['ds'].max() # Dernière date du dataframe

        # Génère les dates de la future période et crée le Dataframe
        dates_futures = pd.date_range(start=last_date + pd.Timedelta(hours=1), periods=120, freq='3h')
        X_future = pd.DataFrame({'ds': dates_futures})

        # Calcule les bornes à prédire
        start_date = dates_futures.min()
        end_date = dates_futures.max()

        # Retire une année aux dates
        start_last_year = start_date - pd.DateOffset(years=1)
        end_last_year = end_date - pd.DateOffset(years=1)

        # Filtre les valeurs historiques sur la dernière année
        mask = (df['ds'] >= start_last_year) & (df['ds'] <= end_last_year)

        temp_last_year = df.loc[mask, 'y']

        temp_last_year = temp_last_year.iloc[:len(dates_futures)].reset_index(drop=True)

        X_future['y'] = temp_last_year.values

        logging.info(f"Historical data: {len(temp_last_year)} vs Future: {len(dates_futures)}")
        return X_future

    def savePredict(self, predict: pd.DataFrame, model_id: str) -> None:
        data_predict_repository = DataPredictTimeseriesRepository(self.db_manager.session)
        data_predict_repository.insert_from_dataframe(predict, model_id)

