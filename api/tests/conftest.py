import pytest
from fastapi.testclient import TestClient
from datetime import datetime, timedelta
from unittest.mock import patch, MagicMock

from api.main import app
from model.entity.data_predict_timeseries import DataPredictTimeseries
from model.entity.data_process_timeseries import DataProcessTimeseries

@pytest.fixture
def client():
    """
    Fournit un client de test FastAPI
    """
    return TestClient(app)

@pytest.fixture
def mock_db_session():
    """
    Simule une session de base de données pour isoler les tests
    """
    with patch('api.main.DatabaseManager') as mock_db_manager:
        mock_session = MagicMock()
        mock_db_manager.return_value.session = mock_session
        mock_db_manager.return_value.init_connection.return_value = None
        yield mock_db_manager

@pytest.fixture
def mock_champion_model():
    """
    Fixture qui simule le modèle champion retourné par le repository
    """
    mock_champion = MagicMock()
    mock_champion.model = "champion_model"
    return mock_champion

@pytest.fixture
def mock_predictions():
    """
    Simule 24 heures de prédictions avec DataPredictTimeseries
    """
    predictions = []
    now = datetime(2025, 6, 20, 0, 0, 0)

    for i in range(24):
        p = DataPredictTimeseries()
        p.ds = now + timedelta(hours=i)
        p.y = 100 + i
        p.model_id = "champion_model_v1"
        predictions.append(p)
    return predictions

@pytest.fixture
def mock_observed_data():
    """
    Simule 24 heures de données réelles avec DataProcessTimeseries
    """
    observed = []
    now = datetime(2025, 6, 20, 0, 0, 0)

    for i in range(24):
        d = DataProcessTimeseries()
        d.ds = now + timedelta(hours=i)
        d.y = 95 + i
        observed.append(d)
    return observed


