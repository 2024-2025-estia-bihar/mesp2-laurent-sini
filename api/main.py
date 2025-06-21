"""
Ce script doit contenir l'implémentation des endpoints pour les fonctionnalités suivantes :
- Génération des prédictions pour une date donnée,
- Récupération des prédictions pour une date donnée,
- Récupération des prédictions combinées avec des données réelles observées pour une période donnée
"""
import os
import platform
from datetime import datetime, time, timedelta
from urllib.parse import unquote

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from sqlalchemy import func

from model.entity.data_predict_timeseries import DataPredictTimeseries
from model.entity.data_process_timeseries import DataProcessTimeseries
from model.helpers.api_helper import location_files_version
from model.repository.logging_timeseries_repository import LoggingTimeseriesRepository
from model.services.database_manager import DatabaseManager
from model.services.secure_logger_manager import SecureLoggerManager

load_dotenv()
api_version = os.getenv("API_VERSION", "0.0.0")
nb_days_predict = 7

secure_log = SecureLoggerManager().get_logger()
app = FastAPI(
    title="MESP2 API",
    description="API de prédiction de séries temporelles météo (projet MESP2)",
    version=api_version
)

@app.get("/", tags=["Informations"])
async def root():
    """
    Route d'accueil de l'API.
    Donne un aperçu du projet, des endpoints clés et de l'environnement.
    """
    return {
        "projet": "MESP2 Laurent SINI",
        "description": (
            "Système de prédiction de séries temporelles utilisant XGBoost pour prédire la température "
            "à partir de données météorologiques. Pipeline MLOps complet (collecte, entraînement, prédiction, API REST)."
        ),
        "api_version": api_version,
        "python_version": platform.python_version(),
        "endpoints": [
            {"path": "/docs", "description": "Documentation Swagger"},
            {"path": "/predictions/{date}", "description": "Prédictions pour une date donnée"},
            {"path": "/predictions/combined/{start_date}/{end_date}", "description": "Données combinées (réelles + prédictions)"},
            {"path": "/version", "description": "Version de l’API"},
        ],
        "contact": "contact@thodler.art"
    }

@app.get("/predictions/combined/{start_date}/{end_date}", responses={
             200: {"description": "Données combinées récupérées avec succès"},
             400: {"description": "Format de date invalide. Utiliser YYYY-MM-DD"}
         })
async def combined_predictions(start_date: str, end_date: str):
    """
    Récupère les données combinées (valeurs observées et prédictions du meilleur modèle) pour une période donnée.

    - **start_date** : Date de début au format YYYY-MM-DD (exemple: 2025-06-01)
    - **end_date** : Date de fin au format YYYY-MM-DD (exemple: 2025-06-07)
    - **Retourne** : Une liste d'objets contenant, pour chaque timestamp, la valeur réelle observée et la prédiction associée.
    """

    db_manager = DatabaseManager()
    try:
        db_manager.init_connection()
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
        start_dt_dt = datetime.combine(start_dt, time.min)
        end_dt_dt = datetime.combine(end_dt, time.max)

        # Récupérer le modèle champion
        champion = LoggingTimeseriesRepository(db_manager.session).get_best_model()

        latest_model_query = (
            db_manager.session.query(
                DataPredictTimeseries.model_id,
                func.max(DataPredictTimeseries.created_at).label('max_created_at')
            )
            .filter(DataPredictTimeseries.model_id.contains(champion.model))
            .group_by(DataPredictTimeseries.model_id)
            .order_by(func.max(DataPredictTimeseries.created_at).desc())
            .limit(1)
            .subquery()
        )

        # Récupérer les données réelles pour ces timestamps exacts
        observed = (
            db_manager.session.query(DataProcessTimeseries)
            .filter(
                DataProcessTimeseries.ds >= start_dt_dt,
                DataProcessTimeseries.ds <= end_dt_dt
            )
            .all()
        )

        # Récupérer les prédictions
        predicts = (
            db_manager.session.query(DataPredictTimeseries)
            .filter(
                DataPredictTimeseries.ds >= start_dt_dt,
                DataPredictTimeseries.ds <= end_dt_dt,
                DataPredictTimeseries.model_id == latest_model_query.c.model_id
            )
            .all()
        )

        # Construire la réponse combinée
        combined_list = []
        for obs in observed:
            pred = next((p.y for p in predicts if p.ds == obs.ds), None)
            item = {
                "ds": obs.ds.isoformat(),
                "y_pred": pred ,
                "y": obs.y
            }
            combined_list.append(item)

        return {"combined": combined_list}

    except ValueError as e:
        secure_log.error(e)
        raise HTTPException(status_code=400, detail="Format de date invalide. Utilisez YYYY-MM-DD")

    except Exception as e:
        secure_log.error(e)
        return {"combined": [], "error": str(e)}
    finally:
        secure_log.info("Fin de combined_predictions")
        db_manager.session.close()



@app.get("/predictions/{date:path}", responses={
    400: {"description": "La date est dans le passé ou trop loin dans le futur"},
    200: {"description": "Prédictions récupérées avec succès"}
})
async def predictions(date: str):
    """
    Récupère les prédictions pour une date donnée.
    - **date** : La date au format YYYY-MM-DD (exemple : 2025-06-20)
    """

    decoded_date = unquote(date)
    date = decoded_date.replace("/", "-")

    db_manager = DatabaseManager()
    try:
        db_manager.init_connection()

        target_date = datetime.strptime(date, "%Y-%m-%d").date()
        today = target_date.today()

        if target_date < today:
            raise HTTPException(status_code=400, detail="Les dates passées ne sont pas des prédictions")

        max_future_date = today + timedelta(days=nb_days_predict)
        if target_date > max_future_date:
            raise HTTPException(
                status_code=400,
                detail=f"Aucune prévision disponible pour cette date. Remonter à {nb_days_predict} jours maximum dans le futur."
            )

        start_dt = datetime.combine(target_date, time.min)
        end_dt = datetime.combine(target_date, time.max)

        champion = LoggingTimeseriesRepository(db_manager.session).get_best_model()

        latest_model_query = (
            db_manager.session.query(
                DataPredictTimeseries.model_id,
                func.max(DataPredictTimeseries.created_at).label('max_created_at')
            )
            .filter(
                DataPredictTimeseries.model_id.contains(champion.model)
            )
            .group_by(DataPredictTimeseries.model_id)
            .order_by(func.max(DataPredictTimeseries.created_at).desc())
            .limit(1)
            .subquery()
        )

        predicts = (
            db_manager.session.query(DataPredictTimeseries)
            .filter(
                DataPredictTimeseries.ds >= start_dt,
                DataPredictTimeseries.ds <= end_dt,
                DataPredictTimeseries.model_id == latest_model_query.c.model_id
            )
            .all()
        )

        return {
            "prediction": predicts,
            "count": len(predicts),
        }

    except ValueError as e:
        secure_log.error(e)
        raise HTTPException(status_code=400, detail="Format de date invalide. Utilisez YYYY-MM-DD")

    except HTTPException as e:
        secure_log.error(e)
        raise

    except Exception as e:
        secure_log.error(e)
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        secure_log.info("Fin de predictions")
        db_manager.session.close()

@app.get("/version")
async def version():
    """
    Retourne la version logicielle actuelle de l'API.

    - **En local** : retourne "0.0.0"
    - **En production (build CICD)** : retourne le commit ID du build
    - **Exemple de réponse** : {"version" : "0.0.0"} ou {"version" : "a1b2c3d4"}
    """
    API_VERSION = "0.0.0"
    try:
        with open(location_files_version()) as f:
            API_VERSION = f.read().strip()
    except FileNotFoundError:
        pass # Fichier absent, on garde la valeur par défaut

    return {"version": API_VERSION}
