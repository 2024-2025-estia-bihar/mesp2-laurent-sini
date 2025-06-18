from abc import ABC, abstractmethod

import pandas as pd

class FeatureManagerInterface(ABC):

    @abstractmethod
    def lagger(self, train: pd.DataFrame, test: pd.DataFrame, best_n_lags: int) -> (pd.DataFrame, pd.DataFrame):
        pass

    @abstractmethod
    def transformData(self, train: pd.DataFrame, test: pd.DataFrame):
        pass