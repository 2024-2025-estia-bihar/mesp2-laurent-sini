import os


def location_files_version()->str:
    file = "/app/version.txt"
    env = os.getenv('APP_ENV', 'dev')

    if env == 'dev':
        file = './version.txt'

    return file

def get_version():
    API_VERSION = os.getenv("API_VERSION", "0.0.0")
    try:
        with open(location_files_version()) as f:
            API_VERSION = f.read().strip()
    except FileNotFoundError:
        pass  # Fichier absent, on garde la valeur par défaut

    return API_VERSION