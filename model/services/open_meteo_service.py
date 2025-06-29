from datetime import datetime, timedelta

import openmeteo_requests
import requests_cache
from retry_requests import retry

import pandas as pd

class OpenMeteoService:

    def __init__(self, start_date=None, end_date=None):
        # Définir start_date avec valeur par défaut
        if start_date is None:
            start_date = "2023-01-01"

        # Calculer end_date = hier si non fourni
        if end_date is None:
            end_date = (datetime.today() - timedelta(days=2)).strftime("%Y-%m-%d")

        # Construction dynamique de l'URL
        self.url = f"https://archive-api.open-meteo.com/v1/archive?latitude=52.52&longitude=13.41&hourly=temperature_2m,relative_humidity_2m&start_date={start_date}&end_date={end_date}"

        # Configuration client API
        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.openmeteo = openmeteo_requests.Client(session=retry_session)

    def get_meteo(self):
        try:
            response = self.openmeteo.weather_api(self.url, params={})

            hourly_data = response[0].Hourly()
            temperature_np = hourly_data.Variables(0).ValuesAsNumpy()
            humidity_np = hourly_data.Variables(1).ValuesAsNumpy()

            # Génération des timestamps
            start_time = hourly_data.Time()
            interval = hourly_data.Interval()
            time_stamps = [start_time + i * interval for i in range(len(temperature_np))]

            # Conversion en datetime
            base_date = datetime(1970, 1, 1)
            dates = [base_date + timedelta(seconds=ts) for ts in time_stamps]

            return pd.DataFrame({
                'time': dates,
                'temperature_2m': temperature_np,
                'relative_humidity_2m': humidity_np
            })
        except Exception as e:
            print(f"Erreur API : {e}")
            return None
