"""
Ce script doit contenir l'implémentation des endpoints pour les fonctionnalités suivantes :
- Génération des prédictions pour une date donnée,
- Récupération des prédictions pour une date donnée,
- Récupération des prédictions combinées avec des données réelles observées pour une période donnée
"""
import logging
import os
from datetime import datetime, time

from dotenv import load_dotenv
from fastapi import FastAPI
from sqlalchemy import func

from model.entity.data_predict_timeseries import DataPredictTimeseries
from model.entity.data_process_timeseries import DataProcessTimeseries
from model.repository.logging_timeseries_repository import LoggingTimeseriesRepository
from model.services.database_manager import DatabaseManager

load_dotenv()
api_version = os.getenv("API_VERSION", "0.0.0")

app = FastAPI()

@app.get("/predictions/{date}")
async def predictions(date: str):
    db_manager = DatabaseManager()
    try:
        db_manager.init_connection()

        target_date = datetime.strptime(date, "%Y-%m-%d").date()
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
    except Exception as e:
        logging.error(e)

        return {
            "predictions": [],
            "error": str(e)
        }
    finally:
        logging.info("Fin de predictions")
        db_manager.session.close()


@app.get("/predictions/combined/{start_date}/{end_date}")
async def combined_predictions(start_date: str, end_date: str):
    db_manager = DatabaseManager()
    try:
        db_manager.init_connection()
        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
        start_dt_dt = datetime.combine(start_dt, time.min)
        end_dt_dt = datetime.combine(end_dt, time.max)

        # Récupérer le modèle champion
        champion = LoggingTimeseriesRepository(db_manager.session).get_best_model()

        # Sous-requête pour le dernier modèle
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
            pred = next((p for p in predicts if p.ds == obs.ds), None)

            item = {
                "ds": obs.ds.isoformat(),
                "y_pred": pred.y ,
                "y": obs.y
            }
            combined_list.append(item)

        return {"combined": combined_list}

    except Exception as e:
        logging.error(e)
        return {"combined": [], "error": str(e)}
    finally:
        logging.info("Fin de combined_predictions")
        db_manager.session.close()


@app.get("/version")
async def version():
    return {"version": api_version}
