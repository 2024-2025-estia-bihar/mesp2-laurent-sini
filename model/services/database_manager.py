from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

class DatabaseManager:

    def __init__(self):
        self.engine = None
        self.session = None

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