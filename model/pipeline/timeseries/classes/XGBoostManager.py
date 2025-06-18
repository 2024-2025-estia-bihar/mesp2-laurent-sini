import datetime
import logging

from pathlib import Path
import joblib

import numpy as np
import optuna
import pandas as pd
from feature_engine.timeseries.forecasting import LagFeatures
from sklearn.metrics import mean_squared_error
from sklearn.model_selection import TimeSeriesSplit
from xgboost import XGBRegressor

from model.helpers.open_meteo_helper import metrics_result
from model.pipeline.interface.ModelManagerInterface import ModelManagerInterface
from visualizations.monitoring.monitoring import match_val_predict

optuna.logging.set_verbosity(optuna.logging.WARNING)

class XGBoostManager(ModelManagerInterface):

    def __init__(self):
        self.model = None
        self.params = None
        timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        self.model_id = f"XGBRegressor_{timestamp}"


    def tune(self, train: pd.DataFrame):
        def objective(trial):
            mse_scores = []
            tscv = TimeSeriesSplit(n_splits=3)

            # Paramètres des lag features
            n_lags = trial.suggest_int('n_lags', 1, 10)

            # Paramètres XGBoost
            n_estimators = trial.suggest_int('n_estimators', 50, 300)
            max_depth = trial.suggest_int('max_depth', 3, 8)
            learning_rate = trial.suggest_float('learning_rate', 0.01, 0.3)
            subsample = trial.suggest_float('subsample', 0.6, 1.0)

            train_numeric = train.select_dtypes(include=['number'])

            for train_idx, val_idx in tscv.split(train_numeric):
                train_tss = train_numeric.iloc[train_idx].copy()
                val_tss = train_numeric.iloc[val_idx].copy()

                # Créer les lag features
                lag_transformer = LagFeatures(
                    variables=['y'],
                    periods=list(range(1, n_lags + 1))
                )

                # Appliquer les transformations
                train_transformed = lag_transformer.fit_transform(train_tss).dropna()
                last_n_lags = train_tss.tail(n_lags)
                val_init = pd.concat([last_n_lags, val_tss])

                val_transformed = lag_transformer.transform(val_init).iloc[n_lags:].dropna()

                if train_transformed.empty or val_transformed.empty:
                    continue

                X_train = train_transformed.drop(columns=['y'])
                y_train = train_transformed['y']
                X_val = val_transformed.drop(columns=['y'])
                y_val = val_transformed['y']

                # Entraînement
                model = XGBRegressor(
                    n_estimators=n_estimators,
                    max_depth=max_depth,
                    learning_rate=learning_rate,
                    subsample=subsample,
                    random_state=42
                )

                model.fit(X_train, y_train)

                # Prédiction
                y_pred = model.predict(X_val)
                mse_scores.append(mean_squared_error(y_val, y_pred))

            return np.mean(mse_scores)

        self.params = optuna.create_study(direction='minimize')
        self.params.optimize(objective, n_trials=100, show_progress_bar=True)

    def train(self, X_train: pd.DataFrame, y_train: pd.DataFrame):

        best_params = self.params.best_params
        params = dict(best_params)
        params.pop('n_lags', None)

        self.model = XGBRegressor(**params, random_state=42)
        self.model.fit(X_train, y_train)

    def eval(self, X_test: pd.DataFrame, y_test: pd.DataFrame):
        root = Path(__file__).resolve().parents[4]  # racine du projet
        img_path = root / "monitoring" / "output" / f"{self.model_id}.png"

        predict = self.predict(X_test)

        match_val_predict(predict['y'].values, y_test, 'XGBRegressor').savefig(img_path)

        return metrics_result(predict['y'].values, y_test), predict

    def predict(self, predict: pd.DataFrame):

        dates = predict.index.copy()
        p = self.model.predict(predict)
        return pd.DataFrame({'ds': dates, 'y': p})


    def save(self):
        root = Path(__file__).resolve().parents[3]
        registry = root / "registry" / f"{self.model_id}.joblib"

        joblib.dump(self.model, registry)
        logging.info(f"Modèle sauvegardé : {registry}")

    def loadBestModel(self):
        root = Path(__file__).resolve().parents[3]
        model_id = self.model_id.split('_')
        registry = root / "registry" / f"{model_id[0]}_{model_id[1]}.joblib"
        self.model = joblib.load(registry)