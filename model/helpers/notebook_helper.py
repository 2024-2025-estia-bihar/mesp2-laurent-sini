import datetime


def generate_version(model:str):
    return f"notebook_{model}{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}"