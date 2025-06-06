from sklearn.model_selection import train_test_split

import pandas as pd

def split_time_series(df, train_size=0.7, val_size=0.15, test_size=0.15, datetime_col="time"):
    """
    Split un DataFrame de série temporelle en ensembles train, val et test de façon chronologique.
    Args:
        df (pd.DataFrame): DataFrame trié par la colonne datetime.
        train_size (float): Proportion pour l'entraînement.
        val_size (float): Proportion pour la validation.
        test_size (float): Proportion pour le test.
        datetime_col (str): Nom de la colonne temporelle (par défaut 'time').

    Returns:
        tuple: (df_train, df_val, df_test)
    """
    if abs(train_size + val_size + test_size - 1.0) > 1e-6:
        raise ValueError("Les proportions doivent faire 1.0 au total")

    # Tri par date si ce n'est pas déjà fait
    df = df.sort_values(by=datetime_col).reset_index(drop=True)
    n = len(df)
    n_train = int(n * train_size)
    n_val = int(n * val_size)

    df_train = df.iloc[:n_train]
    df_val = df.iloc[n_train:n_train + n_val]
    df_test = df.iloc[n_train + n_val:]
    return df_train, df_val, df_test

def split_dataframe(df, train_size=0.7, val_size=0.15, test_size=0.15, random_state=42, stratify_col=None):
    """
    Sépare un DataFrame en trois ensembles : train, validation, test.
    Args:
        df (pd.DataFrame): Le DataFrame à splitter.
        train_size (float): Proportion du train (par défaut 0.7).
        val_size (float): Proportion du validation (par défaut 0.15).
        test_size (float): Proportion du test (par défaut 0.15).
        random_state (int): Pour la reproductibilité.
        stratify_col (str): Nom de la colonne pour stratifier (optionnel).

    Returns:
        tuple: (df_train, df_val, df_test)
    """
    if abs(train_size + val_size + test_size - 1.0) > 1e-6:
        raise ValueError("Les proportions doivent faire 1.0 au total")

    stratify = df[stratify_col] if stratify_col else None

    df_train, df_temp = train_test_split(
        df,
        train_size=train_size,
        random_state=random_state,
        stratify=stratify
    )
    # Pour validation et test, on split le reste
    val_ratio = val_size / (val_size + test_size)
    stratify_temp = df_temp[stratify_col] if stratify_col else None

    df_val, df_test = train_test_split(
        df_temp,
        train_size=val_ratio,
        random_state=random_state,
        stratify=stratify_temp
    )
    return df_train, df_val, df_test


def rolling_mean(index, values, window_size=1):
    """
    Calcule la moyenne mobile d'une série de données.

    Parameters:
    -----------
    index : array-like
        L'index des données (généralement les dates)
    values : array-like
        Les valeurs pour lesquelles calculer la moyenne mobile
    window_size : int, default=1
        La taille de la fenêtre pour la moyenne mobile

    Returns:
    --------
    pandas.Series
        Une série pandas contenant la moyenne mobile
    """
    import pandas as pd

    # Créer une série pandas avec les valeurs et l'index fournis
    series = pd.Series(values, index=index)

    # Calculer la moyenne mobile
    rolling_mean = series.rolling(window=window_size).mean()

    return rolling_mean

def nan_interpolation_linear(dataframe, column):
    dataframe[column] = dataframe[column].interpolate(method='linear')
    return dataframe

def extract_object_to_dataframe(objects, column):
    return pd.DataFrame([vars(obj) for obj in objects], columns=column)
