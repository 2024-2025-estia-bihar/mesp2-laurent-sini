import datetime


def generate_version():
    return f"notebook_{datetime.datetime.now().strftime("%Y%m%d%H%M%S")}"