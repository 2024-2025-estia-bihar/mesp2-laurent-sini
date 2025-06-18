import logging

import numpy as np
import pandas as pd
from sklearn.metrics import mean_absolute_percentage_error, mean_squared_error, r2_score, mean_absolute_error


def convert_to_dataframe(data_of_database) -> pd.DataFrame:
    """
    Convertit les données brutes en DataFrame avec renommage des colonnes spécifiques pour 'row'.

    Paramètres:
        data_of_database (list): Données brutes extraites de la base
        table_type (str): Type de table ('row', 'data', 'exogen')

    Retourne:
        pd.DataFrame: DataFrame formaté avec colonnes standardisées
    """

    # Création du DataFrame
    df = pd.DataFrame(data_of_database)

    # Suppression de la colonne id
    df = df.drop(columns=['id'])

    # Conversion des dates en format datetime
    if 'ds' in df.columns:
        df['ds'] = pd.to_datetime(df['ds'])

    return df

def metrics_result(pred, val):

    pred_series = pd.Series(pred, index=val.index)

    mape = mean_absolute_percentage_error(val, pred_series) * 100  # Correct
    mae = mean_absolute_error(val, pred_series)
    rmse = np.sqrt(mean_squared_error(val, pred_series))
    r2 = r2_score(val, pred_series)

    logging.info(f"MAPE : {mape:.1f}% | MAE : {mae:.2f} | RMSE : {rmse:.2f} | R2 : {r2:.2f}")

    return {
        "MAPE": mape,
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2,
    }
