from datetime import datetime

from model.entity.logging_timeseries import LoggingTimeseries
from model.repository.logging_timeseries_repository import LoggingTimeseriesRepository


class LoggerManager:
    def __init__(self, session):
        self.repository = LoggingTimeseriesRepository(session)

    def log_training(self, model_name, score, params, results):
        """Log les paramètres d'entraînement d'un modèle"""
        tuner_logging = LoggingTimeseries(
            timestamp=datetime.now(),
            model=model_name,
            score=score,
            params=params,
            results=results
        )

        self.repository.add(tuner_logging)
        self.repository.session.commit()

        print(f"✅ Logged {model_name} training parameters")
