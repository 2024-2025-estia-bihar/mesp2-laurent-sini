from datetime import datetime, timedelta

import openmeteo_requests
import requests_cache
from retry_requests import retry

import pandas as pd

class OpenMeteoService:

    def __init__(self):
        self.url = "https://archive-api.open-meteo.com/v1/archive?latitude=52.52&longitude=13.41&hourly=temperature_2m&start_date=2023-01-01&end_date=2024-12-31"

        cache_session = requests_cache.CachedSession('.cache', expire_after=3600)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)  # Correction ici
        self.openmeteo = openmeteo_requests.Client(session=retry_session)

    def get_meteo(self):
        try:
            response = self.openmeteo.weather_api(self.url, params={})

            hourly_data = response[0].Hourly()
            temperature_np = hourly_data.Variables(0).ValuesAsNumpy()

            # Génération des timestamps
            start_time = hourly_data.Time()
            interval = hourly_data.Interval()
            time_stamps = [start_time + i * interval for i in range(len(temperature_np))]

            # Conversion en datetime
            base_date = datetime(1970, 1, 1)  # Les timestamps sont en secondes depuis epoch
            dates = [base_date + timedelta(seconds=ts) for ts in time_stamps]

            return pd.DataFrame({
                'time': dates,
                'temperature_2m': temperature_np
            })
        except Exception as e:
            print(f"Erreur API : {e}")
            return None
