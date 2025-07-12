"""
Ce script doit contenir l'implémentation des endpoints pour les fonctionnalités suivantes :
- Génération des prédictions pour une date donnée,
- Récupération des prédictions pour une date donnée,
- Récupération des prédictions combinées avec des données réelles observées pour une période donnée
"""
import os
import platform
from datetime import datetime, time, timedelta, date
from urllib.parse import unquote

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from sqlalchemy import func, and_

from model.entity.data_predict_timeseries import DataPredictTimeseries
from model.entity.data_process_timeseries import DataProcessTimeseries
from model.helpers.api_helper import get_version
from model.repository.logging_timeseries_repository import LoggingTimeseriesRepository
from model.services.database_manager import DatabaseManager
from model.services.secure_logger_manager import SecureLoggerManager

load_dotenv()
api_version = get_version()
nb_days_predict = 7

secure_log = SecureLoggerManager('api').get_logger()
app = FastAPI(
    title="MESP2 API",
    description="API de prédiction de séries temporelles météo (projet MESP2)",
    version=api_version
)

@app.get("/",
         tags=["Informations"],
         responses={
             200: {
                 "description": "Accueil de l'API avec informations système",
                 "content": {
                     "application/json": {
                         "example": {
                             "projet": "MESP2 Laurent SINI",
                             "description": "Système de prédiction de séries temporelles...",
                             "api_version": "v1.2.0",
                             "python_version": "3.10.12",
                             "endpoints": [
                                 {"path": "/docs", "description": "Documentation Swagger"},
                                 {"path": "/predictions/{date}", "description": "Prédictions pour une date donnée"},
                                 {"path": "/predictions/combined/{start_date}/{end_date}", "description": "Données combinées (réelles + prédictions)"},
                                 {"path": "/version", "description": "Version de l'API"},
                             ],
                             "contact": "contact@thodler.art"
                         }
                     }
                 }
             }
         })
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

@app.get("/predictions/combined/{start_date}/{end_date}",
         responses={
             200: {
                 "description": "Données combinées récupérées avec succès",
                 "content": {
                     "application/json": {
                         "example": {
                             "combined": [
                                 {"ds": "2025-06-01T00:00:00", "y": 42.1, "y_pred": 41.8},
                                 {"ds": "2025-06-02T00:00:00", "y": 43.2, "y_pred": 42.9}
                             ]
                         }
                     }
                 }
             },
             400: {
                 "description": (
                     "Requête invalide. Causes possibles :\n"
                     "1. Format de date incorrect (doit être YYYY-MM-DD)\n"
                     "2. Date de début > Date de fin\n"
                     "3. Dates futures ou égales à aujourd'hui"
                 ),
                 "content": {
                     "application/json": {
                         "examples": {
                             "invalid_format": {"value": {"detail": "Format de date invalide. Utilisez YYYY-MM-DD"}},
                             "invalid_order": {"value": {"detail": "La date de début doit être antérieure à la date de fin"}},
                             "future_date": {"value": {"detail": "Les prédictions ne peuvent être faites que sur des dates passées"}}
                         }
                     }
                 }
             }
         })
async def combined_predictions(start_date: str, end_date: str):
    """
    Récupère les données combinées pour une période donnée.

    - **start_date** : Date de début au format YYYY-MM-DD (exemple: 2025-06-01)
    - **end_date** : Date de fin au format YYYY-MM-DD (exemple: 2025-06-07)
    - **Retourne** : Une liste d'objets contenant, pour chaque timestamp, la valeur réelle observée et la prédiction associée.
    """
    db_manager = DatabaseManager()
    try:
        db_manager.init_connection()

        if start_date > end_date:
            raise HTTPException(
                status_code=400,
                detail="La date de début doit être inférieure ou égale à la date de fin."
            )

        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()

        if start_dt >= date.today() or end_dt >= date.today():
            raise HTTPException(status_code=400, detail="Les dates doivent être strictement dans le passé")

        start_dt_dt = datetime.combine(start_dt, time.min)
        end_dt_dt = datetime.combine(end_dt, time.max)

        sub_obs = (
            db_manager.session.query(DataProcessTimeseries.ds)
            .filter(
                DataProcessTimeseries.ds >= start_dt_dt,
                DataProcessTimeseries.ds <= end_dt_dt
            )
            .group_by(DataProcessTimeseries.ds)
            .subquery()
        )

        # Récupérer les données réelles pour ces timestamps exacts
        observed = (
            db_manager.session.query(DataProcessTimeseries)
            .join(
                sub_obs,
                and_(
                    DataProcessTimeseries.ds == sub_obs.c.ds
                )
            )
            .all()
        )

        # Récupérer les prédictions
        sub_pred = (
            db_manager.session.query(
                DataPredictTimeseries.ds,
                func.max(DataPredictTimeseries.created_at).label("max_created_at")
            )
            .filter(
                DataPredictTimeseries.ds >= start_dt_dt,
                DataPredictTimeseries.ds <= end_dt_dt
            )
            .group_by(DataPredictTimeseries.ds)
            .subquery()
        )
        predicts = (
            db_manager.session.query(DataPredictTimeseries)
            .join(
                sub_pred,
                and_(
                    DataPredictTimeseries.ds == sub_pred.c.ds,
                    DataPredictTimeseries.created_at == sub_pred.c.max_created_at
                )
            )
            .all()
        )

        print(observed)
        # Construire la réponse combinée
        combined_list = []
        for obs in observed:
            print(obs.ds, obs.y)
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



@app.get("/predictions/{date:path}",
         responses={
             200: {
                 "description": "Prédictions récupérées avec succès",
                 "content": {
                     "application/json": {
                         "example": {
                             "prediction": [
                                 {"ds": "2025-06-20T00:00:00", "y_pred": 42.1},
                                 {"ds": "2025-06-20T01:00:00", "y_pred": 42.3}
                             ],
                             "count": 2
                         }
                     }
                 }
             },
             400: {
                 "description": (
                     "Requête invalide. Causes possibles :\n"
                     "1. Format de date incorrect (doit être YYYY-MM-DD)\n"
                     "2. Date dans le passé\n"
                     "3. Date trop éloignée dans le futur"
                 ),
                 "content": {
                     "application/json": {
                         "examples": {
                             "invalid_format": {"value": {"detail": "Format de date invalide. Utilisez YYYY-MM-DD"}},
                             "past_date": {"value": {"detail": "Les dates passées ne sont pas des prédictions"}},
                             "future_limit": {"value": {"detail": "Aucune prévision disponible pour cette date. Limite: 7 jours dans le futur"}}
                         }
                     }
                 }
             },
             500: {
                 "description": "Erreur interne du serveur"
             }
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

@app.get("/version",
         responses={
             200: {
                 "description": "Version logicielle de l'API récupérée avec succès",
                 "content": {
                     "application/json": {
                         "examples": {
                             "local": {"value": {"version": "0.0.0"}},
                             "production": {"value": {"version": "a1b2c3d4"}},
                             "tagged": {"value": {"version": "v1.0.0"}}
                         }
                     }
                 }
             }
         })
async def version():
    """
    Retourne la version logicielle actuelle de l'API.

    - **En local** : retourne "0.0.0"
    - **En production (build CICD)** : retourne le commit ID du build ou la version
    - **Exemple de réponse** : {"version" : "0.0.0"} ou {"version" : "a1b2c3d4"} ou {"version" : "v1.0.0"}
    """
    return {"version": api_version}
