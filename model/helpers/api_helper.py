import os


def location_files_version()->str:
    file = "/app/version.txt"
    env = os.getenv('APP_ENV', 'dev')

    if env == 'dev':
        file = './version.txt'

    return file