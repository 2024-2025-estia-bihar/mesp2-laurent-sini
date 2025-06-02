import pandas as pd

def convert_to_dataframe(data_of_database)->pd.DataFrame:
    """
    Convertit une liste de données en DataFrame pandas.

    Paramètres
    ----------
    data_of_database : list
        Liste contenant les données de la base de données. Chaque élément doit correspondre à une ligne.

    Retourne
    -------
    pandas.DataFrame
        DataFrame avec les colonnes 'ds' et 'y' (la colonne 'id' est supprimée).
    """
    df = pd.DataFrame(
        data_of_database,
        columns=['id', 'ds', 'y']  # adapte selon ta table
    ).drop(columns=['id'])
    df['ds'] = pd.to_datetime(df['ds'])
    return df