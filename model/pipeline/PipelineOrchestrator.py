import logging

from model.services.secure_logger_manager import SecureLoggerManager

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s"
)

from model.entity.base import Base
from model.pipeline.interface import ModelManagerInterface
from model.pipeline.interface.DataManagerInterface import DataManagerInterface

from model.pipeline.interface.FeatureManagerInterface import FeatureManagerInterface
from model.pipeline.timeseries.FeatureManager import FeatureManager
from model.pipeline.timeseries.classes.XGBoostManager import XGBoostManager
from model.services.database_manager import DatabaseManager
from model.services.logger_manager import LoggerManager


class PipelineOrchestrator:
    def __init__(self,
                 data_manager: DataManagerInterface,
                 logger_database: LoggerManager,
                 feature_manager: FeatureManagerInterface,
                 model_manager: ModelManagerInterface
                 ):
        self.data_manager = data_manager
        self.feature_manager = feature_manager
        self.model_manager = model_manager
        self.logger_database = logger_database

    def run(self):

        secure_log = SecureLoggerManager('pipeline_orchestrator').get_logger()
        secure_log.info("Lancement du pipeline")

        secure_log.info("Etape 1 - Nettoyage des données")
        df = self.data_manager.loadData()
        df = self.data_manager.cleanData(df)
        df = self.data_manager.transformData(df)

        self.data_manager.saveData(df)
        train, test = self.data_manager.splitData(df)

        secure_log.info("Etape 2 - Recherche des hyperparameters")
        self.model_manager.tune(train)

        secure_log.info("Etape 3 - Recherche des features")
        train, test = self.feature_manager.transformData(train, test)

        best_n_lags=self.model_manager.params.best_params['n_lags']
        X_train, y_train, X_test, y_test = self.feature_manager.lagger(train, test, best_n_lags)

        secure_log.info("Etape 4 - Entrainement")
        self.model_manager.train(X_train, y_train)

        secure_log.info("Etape 5 - Evaluation")
        results, _ = self.model_manager.eval(X_test, y_test)

        secure_log.info("Etape 6 - Results")
        self.model_manager.save()
        secure_log.info(f"Modèle sauvegardé : {self.model_manager.model_id}")
        self.logger_database.log_training(
            'XGBRegressor',
            self.model_manager.params.best_value,
            self.model_manager.params.best_params,
            results,
            self.model_manager.model_id,
        )

        secure_log.info("Finished pipeline")


if __name__ == '__main__':
    from model.pipeline.timeseries.DataManager import DataManager

    db_manager = DatabaseManager()
    db_manager.init_connection()

    logger_manager = LoggerManager(db_manager.session)

    Base.metadata.create_all(db_manager.engine)

    xgb = XGBoostManager()

    pipelineOrchestrator = PipelineOrchestrator(
        data_manager=DataManager(db_manager),
        model_manager=xgb,
        feature_manager=FeatureManager(xgb),
        logger_database=logger_manager
    )

    pipelineOrchestrator.run()