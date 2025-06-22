import json
import logging
import uuid

from model.repository.logging_timeseries_repository import LoggingTimeseriesRepository
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


class PipelineBatchPredictor:
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

        secure_log = SecureLoggerManager('pipeline_batch').get_logger()

        secure_log.info("Lancement du pipeline")

        secure_log.info("Etape 1 - Nettoyage des données")
        df = self.data_manager.loadData()
        df = self.data_manager.cleanData(df)
        df = self.data_manager.transformData(df)

        secure_log.info("Etape 2 - Transformation des données")
        data_future = self.data_manager.loadFutureData(df)
        train_future, test_future = self.feature_manager.transformData(df, data_future)

        best_n_lags = self.model_manager.params['n_lags']
        X_train, y_train, X_test, y_test = self.feature_manager.lagger(train_future, test_future, best_n_lags)

        secure_log.info("Etape 3 - Evaluation")
        self.model_manager.loadBestModel()
        results, predict = self.model_manager.eval(X_test, y_test)

        self.data_manager.savePredict(predict, self.model_manager.model_id)

        secure_log.info("Finished pipeline")

if __name__ == '__main__':
    from model.pipeline.timeseries.DataManager import DataManager

    db_manager = DatabaseManager()
    db_manager.init_connection()

    logger_manager = LoggerManager(db_manager.session)

    Base.metadata.create_all(db_manager.engine)

    logging_timeseries_repository = LoggingTimeseriesRepository(db_manager.session)

    xgb = XGBoostManager()
    best_model = logging_timeseries_repository.get_best_model()

    xgb.model_id = best_model.model_id + '_'+ str(uuid.uuid4())
    xgb.params = best_model.params

    PipelineBatchPredictor = PipelineBatchPredictor(
        data_manager=DataManager(db_manager),
        model_manager=xgb,
        feature_manager=FeatureManager(xgb),
        logger_database=logger_manager
    )

    PipelineBatchPredictor.run()

    db_manager.session.close()