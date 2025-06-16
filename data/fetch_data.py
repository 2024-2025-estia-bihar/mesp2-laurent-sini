import os

import sys
from datetime import datetime, timedelta

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

print("Connexion à la base de données...")
db_manager = DatabaseManager()
db_manager.init_connection()

try:
    Base.metadata.create_all(db_manager.engine)

except Exception as e:
    print("Erreur lors de la connexion à la base de données:", e)
    print("Vérifiez que les containers sont bien démarrés et que les paramètres de connexion sont corrects.")
    db_manager.close()

data_reel_repository = DataReelTimeseriesRepository(db_manager.session)
last_row = data_reel_repository.get_last_row()

if last_row is not None:
    start_date = last_row.time + timedelta(days=1)
    end_date = (datetime.today() - timedelta(days=2)).date()

    if start_date.date() >= end_date:
        print("Les données sont déjà à jour. Arrêt du script.")
        db_manager.close()
        sys.exit()

    start_date = start_date.strftime("%Y-%m-%d")
else:
    start_date = None

print("Récupération des données de l'API")
open_meteo_service = OpenMeteoService(start_date=start_date)
df_fetch = open_meteo_service.get_meteo()

print("Enregistrement dans la base de données.")
data_reel_repository.insert_from_dataframe(df_fetch)

db_manager.close()

print("Script terminé avec succès.")


