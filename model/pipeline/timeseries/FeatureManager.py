from typing import Any

import pandas as pd
from feature_engine.timeseries.forecasting import LagFeatures

from model.pipeline.interface import ModelManagerInterface
from model.pipeline.interface.FeatureManagerInterface import FeatureManagerInterface


class FeatureManager(FeatureManagerInterface):

    def __init__(self, model_manager: ModelManagerInterface):
        self.model_manager = model_manager

    def transformData(self, train: pd.DataFrame, test: pd.DataFrame):
        train = train.copy()
        test = test.copy()

        if 'relative_humidity_2m' in train.columns:
            train.drop('relative_humidity_2m', axis=1, inplace=True)
        if 'relative_humidity_2m' in test.columns:
            test.drop('relative_humidity_2m', axis=1, inplace=True)

        assert 'ds' in train.columns, "Colonne 'ds' absente de train"
        assert 'ds' in test.columns, "Colonne 'ds' absente de test"

        train.set_index('ds', inplace=True)
        test.set_index('ds', inplace=True)

        train = train.select_dtypes(include=['number'])
        test = test.select_dtypes(include=['number'])

        return train, test

    def lagger(self, train: pd.DataFrame, test: pd.DataFrame, best_n_lags: int) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame, pd.DataFrame]:

        lagger = LagFeatures(
            variables=['y'],
            periods=list(range(1, best_n_lags + 1)),
            sort_index=False
        )

        train_lagger = lagger.fit_transform(train).dropna()
        last_n_lags = train.tail(best_n_lags)

        test_lagger = pd.concat([last_n_lags, test])
        test_lagger = lagger.transform(test_lagger).iloc[best_n_lags:].dropna()

        X_train = train_lagger.drop(columns=['y'])
        y_train = train_lagger['y']

        X_test = test_lagger.drop(columns=['y'])
        y_test = test_lagger['y']

        return X_train, y_train, X_test, y_test