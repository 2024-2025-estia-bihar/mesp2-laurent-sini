from model.entity.base import Base
from model.pipeline.interface.DataManagerInterface import DataManagerInterface
from model.services.database_manager import DatabaseManager


class PipelineOrchestrator:
    def __init__(self, data_manager :DataManagerInterface):
        self.data_manager = data_manager

    def run(self):
        print("Starting pipeline")
        df = self.data_manager.loadData()
        df = self.data_manager.cleanData(df)
        df = self.data_manager.transformData(df)
        self.data_manager.saveData(df)


        print("Finished pipeline")


if __name__ == '__main__':
    from model.pipeline.timeseries.DataManager import DataManager

    db_manager = DatabaseManager()
    db_manager.init_connection()

    Base.metadata.create_all(db_manager.engine)

    pipelineOrchestrator = PipelineOrchestrator(
        data_manager=DataManager(db_manager)
    )

    pipelineOrchestrator.run()