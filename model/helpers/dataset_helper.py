import pandas as pd

def nan_interpolation_linear(dataframe, column):
    dataframe[column] = dataframe[column].interpolate(method='linear')
    return dataframe

def extract_object_to_dataframe(objects, column):
    return pd.DataFrame([vars(obj) for obj in objects], columns=column)
