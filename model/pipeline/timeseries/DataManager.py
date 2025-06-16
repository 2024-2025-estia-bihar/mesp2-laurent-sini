import pandas as pd

from model.helpers.dataset_helper import extract_object_to_dataframe, nan_interpolation_linear
from model.pipeline.interface.DataManagerInterface import DataManagerInterface
from model.repository.data_process_timeseries_repository import DataProcessTimeSeriesRepository
from model.repository.data_reel_timeseries_repository import DataReelTimeseriesRepository
from model.services.database_manager import DatabaseManager


class DataManager(DataManagerInterface):

    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    def loadData(self) -> pd.DataFrame:
        print("Loading data")
        data_reel_repository = DataReelTimeseriesRepository(self.db_manager.session)
        return extract_object_to_dataframe(data_reel_repository.getAll(), ['time', 'temperature_2m', 'relative_humidity_2m'])

    def cleanData(self, df: pd.DataFrame) -> pd.DataFrame :
        print("Cleaning data")
        df = nan_interpolation_linear(df, 'time')
        return df

    def transformData(self, df: pd.DataFrame) -> pd.DataFrame :
        df = df.rename(columns={'time': 'ds', 'temperature_2m': 'y'})
        return df

    def saveData(self, df: pd.DataFrame) -> None:
        data_process_repository = DataProcessTimeSeriesRepository(self.db_manager.session)
        data_process_repository.insert_from_dataframe(df)
