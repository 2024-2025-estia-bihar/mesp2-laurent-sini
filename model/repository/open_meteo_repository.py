import logging
import sqlite3


class OpenMeteoRepository:
    def __init__(self, db_path='../data/meteo_data.db'):
        self.db_path = db_path
        self.logger = logging.getLogger(__name__)
        self._init_db()

    def _init_db(self):
        """Initialise la structure de la base selon les spécifications TPT"""
        with self._get_connection() as conn:
            conn.execute('''
                CREATE TABLE IF NOT EXISTS row (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME UNIQUE,
                    temperature_2m REAL
                )
            ''')
            conn.execute('''
                CREATE TABLE IF NOT EXISTS data (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    ds DATETIME UNIQUE,
                    y REAL
                )
            ''')

    def _get_connection(self):
        """Crée une nouvelle connexion à la base"""
        return sqlite3.connect(self.db_path)

    def insert_raw_data(self, df):
        """
        Insère les données d'un DataFrame pandas dans SQLite

        Args:
            df: DataFrame avec colonnes 'time' (datetime) et 'temperature_2m'
        """
        try:
            # Conversion des données en tuples (timestamp ISO, température)
            data = [
                (dt.isoformat(), temp)
                for dt, temp in zip(df['time'], df['temperature_2m'])
            ]

            with self._get_connection() as conn:
                conn.executemany('''
                    INSERT OR IGNORE INTO row 
                    (timestamp, temperature_2m) 
                    VALUES (?, ?)
                ''', data)
                conn.commit()

            self.logger.info(f"Insertion réussie de {len(data)} mesures")

        except KeyError as e:
            self.logger.error(f"Colonne manquante: {str(e)}")
            raise ValueError("Le DataFrame doit contenir les colonnes 'time' et 'temperature_2m'")
        except Exception as e:
            self.logger.error(f"Erreur d'insertion: {str(e)}")
            raise

    def insert_data(self, df):
        """
        Insère les données d'un DataFrame pandas dans SQLite

        Args:
            df: DataFrame avec colonnes 'ds' (datetime) et 'y' (mesures)
        """
        try:
            data = [
                (dt.isoformat(), temp)
                for dt, temp in zip(df['ds'], df['y'])
            ]

            with self._get_connection() as conn:
                conn.executemany('''
                    INSERT OR IGNORE INTO data 
                    (ds, y) 
                    VALUES (?, ?)
                ''', data)
                conn.commit()

            self.logger.info(f"Insertion réussie de {len(data)} mesures")

        except KeyError as e:
            self.logger.error(f"Colonne manquante: {str(e)}")
            raise ValueError("Le DataFrame doit contenir les colonnes 'ds' et 'y'")
        except Exception as e:
            self.logger.error(f"Erreur d'insertion: {str(e)}")
            raise

    def find_all_by_table(self, table):
        """
        Récupère toutes les lignes d'une table donnée.

        Args:
            table (str): Nom de la table ('row' ou 'data_processed').

        Returns:
            list of tuple: Toutes les lignes de la table.
        """
        # Sécurisation du nom de table pour éviter l'injection SQL
        if table not in ('row', 'data'):
            raise ValueError("Table inconnue")
        sql = f"SELECT * FROM {table}"
        with self._get_connection() as conn:
            cursor = conn.execute(sql)
            return cursor.fetchall()


