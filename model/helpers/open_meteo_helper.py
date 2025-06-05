import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error, r2_score, mean_absolute_error


def convert_to_dataframe(data_of_database, table_type: str) -> pd.DataFrame:
    """
    Convertit les données brutes en DataFrame avec renommage des colonnes spécifiques pour 'row'.

    Paramètres:
        data_of_database (list): Données brutes extraites de la base
        table_type (str): Type de table ('row', 'data', 'exogen')

    Retourne:
        pd.DataFrame: DataFrame formaté avec colonnes standardisées
    """

    # Mapping des colonnes selon la table
    columns_map = {
        'row': ['id', 'timestamp', 'temperature_2m', 'relative_humidity_2m'],
        'data': ['id', 'ds', 'y'],
        'exogen': ['id', 'ds', 'relative_humidity_2m']
    }

    # Création du DataFrame
    df = pd.DataFrame(data_of_database, columns=columns_map[table_type])

    # Suppression de la colonne id
    df = df.drop(columns=['id'])

    # Renommage des colonnes pour la table 'row'
    if table_type == 'row':
        df = df.rename(columns={
            'timestamp': 'ds',
            'temperature_2m': 'y'
        })

    # Conversion des dates en format datetime
    if 'ds' in df.columns:
        df['ds'] = pd.to_datetime(df['ds'])

    return df

def metrics_result(forcast, val):

    mape = mean_absolute_percentage_error(val['y'], forcast.predicted_mean) * 100  # Correct
    mae = mean_absolute_error(val['y'], forcast.predicted_mean)
    rmse = np.sqrt(mean_squared_error(val['y'], forcast.predicted_mean))
    r2 = r2_score(val['y'], forcast.predicted_mean)

    print(f"MAPE : {mape:.1f}%")
    print(f"MAE : {mae:.2f}")  # Unités originales
    print(f"RMSE : {rmse:.2f}")
    print(f"R² : {r2:.3f}")  # Entre 0 et 1