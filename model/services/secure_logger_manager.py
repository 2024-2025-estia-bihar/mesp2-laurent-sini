import logging
import os
from logging.handlers import RotatingFileHandler
from pathlib import Path

from model.helpers.api_helper import get_version


class SecureLoggerManager:
    def __init__(self, application_logger: str):
        self.application_logger = application_logger

        self.logger = logging.getLogger(self.application_logger)
        self.logger.setLevel(logging.INFO)

        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

        log_path = Path(f"monitoring/logs/{self.application_logger}.log")
        log_path.parent.mkdir(parents=True, exist_ok=True)

        file_handler = RotatingFileHandler(
            log_path,
            maxBytes=1000000,
            backupCount=10,
            encoding='utf-8'
        )
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)

        if self._is_loki_enabled():
            self._add_loki_handler(formatter)

    def _is_loki_enabled(self):
        """Vérifie la configuration Loki sécurisée"""
        loki_url = os.getenv('LOKI_URL')
        loki_user = os.getenv('LOKI_USER')
        loki_password = os.getenv('LOKI_PASSWORD')

        return loki_url and loki_user and loki_password

    def _add_loki_handler(self, formatter):
        """Ajoute la handler Loki de manière sécurisée"""
        try:
            from logging_loki import LokiHandler

            handler = LokiHandler(
                url=os.getenv('LOKI_URL') + "/loki/api/v1/push",
                auth=(os.getenv("LOKI_USER"), os.getenv("LOKI_PASSWORD")),
                tags={
                    "service": self.application_logger,
                    "env": os.getenv('APP_ENV', 'dev'),
                    "api_version": get_version()
                },
                version="1"
            )

            handler.setFormatter(formatter)
            self.logger.addHandler(handler)
            self.logger.info("Loki handle activé")
        except ImportError:
            self.logger.error("Loki n'existe pas")
        except Exception as e:
            self.logger.error(f"Erreur Loki: {str(e)}")

    def get_logger(self):
        return self.logger