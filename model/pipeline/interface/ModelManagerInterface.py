from abc import ABC, abstractmethod
import pandas as pd

class ModelManagerInterface(ABC):
    """
    Interface abstraite définissant les opérations standard pour la gestion des modèles de machine learning.

    Notes
    -----
    Toute classe concrète implémentant cette interface doit fournir une implémentation
    complète des méthodes de cycle de vie des modèles.
    """

    @abstractmethod
    def tune(self, train: pd.DataFrame):
        """
        Optimise les hyperparamètres du modèle selon une stratégie définie.

        Returns
        -------
        pd.DataFrame
            DataFrame contenant les résultats du tuning (métriques par combinaison d'hyperparamètres).

        Notes
        -----
        Doit implémenter une méthode de recherche (grid search, random search, etc.)
        et retourner un comparatif des performances.
        """
        pass

    @abstractmethod
    def train(self, X_train: pd.DataFrame, y_train: pd.DataFrame) -> pd.DataFrame:
        """
        Entraîne le modèle sur les données préparées.

        Returns
        -------
        pd.DataFrame
            DataFrame contenant les métriques d'entraînement et caractéristiques du modèle.

        Notes
        -----
        Doit gérer le splitting train/validation et l'application des hyperparamètres optimaux.
        """
        pass

    @abstractmethod
    def eval(self, X_test: pd.DataFrame, y_test: pd.DataFrame) -> pd.DataFrame:
        """
        Évalue les performances du modèle sur un jeu de données de test.

        Parameters
        ----------
        data : pd.DataFrame
            Données de test pré-traitées avec les features nécessaires

        Returns
        -------
        pd.DataFrame
            DataFrame contenant les métriques d'évaluation (MAE, RMSE, R², etc.)

        Notes
        -----
        Doit calculer des métriques pertinentes pour le type de modèle implémenté.
        """
        pass

    @abstractmethod
    def save(self) -> pd.DataFrame:
        """
        Persiste le modèle entraîné dans un format réutilisable.

        Parameters
        ----------
        data : pd.DataFrame
            Données nécessaires à la sérialisation (ex: configuration du modèle)

        Returns
        -------
        pd.DataFrame
            Logs de sauvegarde et métadonnées techniques

        Notes
        -----
        Doit gérer la sérialisation dans un format standard (pickle, ONNX, etc.)
        avec versioning des artefacts.
        """
        pass
