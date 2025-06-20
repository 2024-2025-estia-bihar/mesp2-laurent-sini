import logging
import os
from pathlib import Path

import dotenv
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import sessionmaker

dotenv.load_dotenv()

class DatabaseManager:

    def __init__(self):
        self.engine = None
        self.session = None
        self.app_env = os.getenv("APP_ENV", "dev")

    def init_connection(self):
        try:
            """Initialise la connexion selon l'environnement"""
            if self.app_env == "prod":
                self.connect_postgres(
                    user=os.getenv('POSTGRES_USER'),
                    password=os.getenv('POSTGRES_PASSWORD'),
                    host=os.getenv('POSTGRES_HOST'),
                    database=os.getenv('POSTGRES_DB')
                )
            else:
                root = Path(__file__).resolve().parents[2]  # racine du projet
                sqlite_path = root / "data" / "open_meteo.db"

                self.connect_sqlite(str(sqlite_path))
        except OperationalError as e:
            logging.error(f"Erreur de connexion à la base de données : {e}")
            raise
        except Exception as e:
            logging.error(f"Erreur inattendue lors de l'initialisation de la connexion : {e}")
            raise

    def connect_sqlite(self, db_path="open_meteo.db"):
        """Connexion SQLite"""
        self.engine = create_engine(f"sqlite:///{db_path}")
        self.session = sessionmaker(bind=self.engine)()
        return self.session

    def connect_postgres(self, user, password, host, database):
        """Connexion PostgreSQL"""
        url = f"postgresql://{user}:{password}@{host}:5432/{database}"
        self.engine = create_engine(url)
        self.session = sessionmaker(bind=self.engine)()
        return self.session

    def close(self):
        """Fermer la connexion"""
        if self.session:
            self.session.close()