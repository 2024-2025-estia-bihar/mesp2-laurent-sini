import logging
import os

import sys
from datetime import datetime, timedelta

from model.services.secure_logger_manager import SecureLoggerManager

sys.path.append("./")

from dotenv import load_dotenv

from model.entity.base import Base

from model.repository.data_reel_timeseries_repository import DataReelTimeseriesRepository
from model.repository.data_process_timeseries_repository import DataProcessTimeSeriesRepository
from model.repository.data_predict_timeseries_repository import DataPredictTimeseriesRepository
from model.repository.logging_timeseries_repository import LoggingTimeseriesRepository

from model.services.database_manager import DatabaseManager
from model.services.open_meteo_service import OpenMeteoService

# Chargement des variables d'environnement postgres
load_dotenv()

app_env = os.getenv("APP_ENV", "dev")

secure_logger = SecureLoggerManager('initialisation').get_logger()

secure_logger.info("Connexion à la base de données...")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

db_manager = DatabaseManager()
db_manager.init_connection()


try:
    Base.metadata.create_all(db_manager.engine)

except Exception as e:
    secure_logger.error("Erreur lors de la connexion à la base de données:", e)
    print("Vérifiez que les containers sont bien démarrés et que les paramètres de connexion sont corrects.")
    db_manager.close()

data_reel_repository = DataReelTimeseriesRepository(db_manager.session)
last_row = data_reel_repository.get_last_row()

if last_row is not None:
    start_date = last_row.time + timedelta(days=1)
    print(start_date)
    end_date = (datetime.today() - timedelta(days=2)).date()
    print(start_date)

    if start_date.date() > end_date:
        secure_logger.warning("Les données sont déjà à jour. Arrêt du script.")
        db_manager.close()
        sys.exit()

    start_date = start_date.strftime("%Y-%m-%d")
else:
    start_date = None

secure_logger.info("Récupération des données de l'API")
open_meteo_service = OpenMeteoService(start_date=start_date)
df_fetch = open_meteo_service.get_meteo()

secure_logger.info("Enregistrement dans la base de données.")
data_reel_repository.insert_from_dataframe(df_fetch)

db_manager.close()

secure_logger.info("Script terminé avec succès.")


