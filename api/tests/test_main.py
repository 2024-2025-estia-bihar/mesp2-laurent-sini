from api.main import app

from datetime import datetime, timedelta
from fastapi.testclient import TestClient
from unittest.mock import patch


client = TestClient(app)

def test_predictions_success(client, mock_db_session, mock_champion_model, mock_predictions):
    """
    Test de succès pour l'endpoint /predictions/{date}
    """
    with patch('api.main.LoggingTimeseriesRepository') as mock_repo:
        mock_repo.return_value.get_best_model.return_value = mock_champion_model
        mock_db_session.return_value.session.query.return_value.filter.return_value.all.return_value = mock_predictions

        future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

        response = client.get(f"/predictions/{future_date}")

        assert response.status_code == 200
        assert "prediction" in response.json()
        assert "count" in response.json()
        assert response.json()["count"] == len(mock_predictions)


def test_predictions_past_date(client):
    """
    Test avec une date passée pour l'endpoint /predictions/{date}
    """
    past_date = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

    response = client.get(f"/predictions/{past_date}")

    assert response.status_code == 400
    assert "Les dates passées ne sont pas des prédictions" in response.json()["detail"]


def test_predictions_too_far_future(client):
    """
    Test avec une date trop lointaine pour l'endpoint /predictions/{date}
    """
    far_future_date = (datetime.now() + timedelta(days=10)).strftime("%Y-%m-%d")

    response = client.get(f"/predictions/{far_future_date}")

    assert response.status_code == 400
    assert "Aucune prévision disponible pour cette date" in response.json()["detail"]


def test_predictions_invalid_date_format(client):
    """
    Test avec un format de date invalide pour l'endpoint /predictions/{date}
    """
    invalid_date = "2025/20/06"

    response = client.get(f"/predictions/{invalid_date}")

    assert response.status_code == 400
    assert "Format de date invalide" in response.json()["detail"]


def test_combined_predictions_success(client, mock_db_session, mock_champion_model, mock_predictions,
                                      mock_observed_data):

    mock_db_session.return_value.session.query.return_value.join.return_value.all.side_effect = [
        mock_observed_data,
        mock_predictions
    ]

    start_date = "2025-06-20"
    end_date = "2025-06-21"

    response = client.get(f"/predictions/combined/{start_date}/{end_date}")

    assert response.status_code == 200
    assert "combined" in response.json()
    assert len(response.json()["combined"]) == len(mock_observed_data)

    first_item = response.json()["combined"][0]
    assert "ds" in first_item
    assert "y" in first_item
    assert "y_pred" in first_item


def test_combined_predictions_invalid_date_format(client):
    """
    Test avec un format de date invalide pour l'endpoint /predictions/combined/{start_date}/{end_date}
    """

    invalid_start_date = "2025/06/20"
    valid_end_date = "2025-06-21"

    response = client.get(f"/predictions/combined/{invalid_start_date}/{valid_end_date}")

    assert response.status_code == 400
    assert "Format de date invalide" in response.json()["detail"]


def test_predictions_database_error(client, mock_db_session):
    """
    Test de gestion d'erreur de base de données pour l'endpoint /predictions/{date}
    """
    mock_db_session.return_value.init_connection.side_effect = Exception("Erreur de connexion à la base de données")

    future_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    response = client.get(f"/predictions/{future_date}")

    assert response.status_code == 500
    assert "Erreur de connexion à la base de données" in response.json()["detail"]


def test_combined_predictions_database_error(client, mock_db_session):
    """
    Test de gestion d'erreur de base de données pour l'endpoint /predictions/combined/{start_date}/{end_date}
    """
    mock_db_session.return_value.init_connection.side_effect = Exception("Erreur de connexion à la base de données")

    start_date = datetime.now().strftime("%Y-%m-%d")
    end_date = (datetime.now() + timedelta(days=1)).strftime("%Y-%m-%d")

    response = client.get(f"/predictions/combined/{start_date}/{end_date}")

    assert "error" in response.json()
    assert "Erreur de connexion à la base de données" in response.json()["error"]

def test_version():
    response = client.get("/version")
    assert response.status_code == 200
    assert "version" in response.json()

