from datetime import datetime

from model.entity.logging_open_meteo import TunerLoggingOpenMeteo
from model.repository.logging_open_meteo_repository import LoggingOpenMeteoRepository


class LoggerManager:
    def __init__(self, session):
        self.repository = LoggingOpenMeteoRepository(session)

    def log_training(self, model_name, score, params, results):
        """Log les paramètres d'entraînement d'un modèle"""
        tuner_logging = TunerLoggingOpenMeteo(
            timestamp=datetime.now(),
            model=model_name,
            score=score,
            params=params,
            results=results
        )

        self.repository.add(tuner_logging)
        self.repository.session.commit()

        print(f"✅ Logged {model_name} training parameters")
