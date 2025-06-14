import os

import sys
from datetime import datetime, timedelta

sys.path.append("./")

import pandas as pd

from model.helpers.dataset_helper import nan_interpolation_linear

from dotenv import load_dotenv

from model.entity.base import Base
from model.repository.data_reel_timeseries_repository import DataReelTimeseriesRepository

from model.services.database_manager import DatabaseManager
from model.services.open_meteo_service import OpenMeteoService

load_dotenv()

db_user = os.getenv("POSTGRES_USER")
db_password = os.getenv("POSTGRES_PASSWORD")
db_host = os.getenv("POSTGRES_HOST")
db_database = os.getenv("POSTGRES_DATABASE")


print("Connexion à la base de données...")
db_manager = DatabaseManager()

try:
    db_manager.connect_postgres(db_user, db_password, db_host, db_database)

    Base.metadata.create_all(db_manager.engine)
except Exception as e:
    print("Erreur lors de la connexion à la base de données:", e)
    print("Vérifiez que les containers sont bien démarrés et que les paramètres de connexion sont corrects.")
    db_manager.close()

data_reel_repository = DataReelTimeseriesRepository(db_manager.session)
last_row = data_reel_repository.get_last_row()

if last_row is not None:
    start_date = last_row.ds + timedelta(days=1)
    end_date = (datetime.today() - timedelta(days=2)).date()

    if start_date.date() >= end_date:
        print("Les données sont déjà à jour. Arrêt du script.")
        db_manager.close()
        sys.exit()
else:
    start_date = None

open_meteo_service = OpenMeteoService(start_date=start_date.strftime("%Y-%m-%d"))

df_fetch = open_meteo_service.get_meteo()

df_fetch = df_fetch.rename(columns={"time": "ds", "temperature_2m": "y"})
df_fetch['ds'] = pd.to_datetime(df_fetch['ds'])

df_fetch = nan_interpolation_linear(df_fetch, 'y')
df_fetch = nan_interpolation_linear(df_fetch, 'relative_humidity_2m')

df_fetch = df_fetch.set_index('ds')
df_fetch = df_fetch.resample('3h').mean()
df_fetch = df_fetch.reset_index()


data_reel_repository.insert_from_dataframe(df_fetch)
db_manager.close()


