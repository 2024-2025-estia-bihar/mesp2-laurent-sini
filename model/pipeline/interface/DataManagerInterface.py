from abc import ABC, abstractmethod

import pandas as pd

from model.services.database_manager import DatabaseManager


class DataManagerInterface(ABC):
    """
    Interface abstraite définissant les opérations standard pour la gestion des données.

    Notes
    -----
    Toute classe héritant de DataManagerInterface doit implémenter toutes les méthodes abstraites.
    """

    @abstractmethod
    def loadData(self) -> pd.DataFrame:
        """
        Méthode abstraite pour le chargement des données.

        Notes
        -----
        Cette méthode doit être implémentée pour charger les données à partir d'une source.
        """
        pass

    @abstractmethod
    def cleanData(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Méthode abstraite pour le nettoyage des données.

        Notes
        -----
        Cette méthode doit être implémentée pour nettoyer les données brutes.
        """
        pass

    @abstractmethod
    def transformData(self, data: pd.DataFrame) -> pd.DataFrame:
        """
        Méthode abstraite pour la transformation des données.

        Notes
        -----
        Cette méthode doit être implémentée pour transformer les données nettoyées en format utilisable.
        """
        pass

    @abstractmethod
    def saveData(self, df: pd.DataFrame) -> None:
        """
        Méthode abstraite pour la sauvegarde des données.

        Notes
        -----
        Cette méthode doit être implémentée pour sauvegarder les données transformées.
        """
        pass

    @abstractmethod
    def splitData(self, df: pd.DataFrame) -> (pd.DataFrame, pd.DataFrame):
        pass

    @abstractmethod
    def loadFutureData(self, df: pd.DataFrame) -> pd.DataFrame:
        pass

    @abstractmethod
    def savePredict(self, predict: pd.DataFrame, model_id: str) -> None:
        pass