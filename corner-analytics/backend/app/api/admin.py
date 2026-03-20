"""Admin endpoints — manual data refresh trigger."""
from fastapi import APIRouter, BackgroundTasks, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.services.api_football import APIFootballClient
from app.services.data_ingestion import (
    sync_teams,
    sync_upcoming_fixtures,
    sync_finished_results,
    ingest_statsbomb_history,
)

router = APIRouter()


def _full_refresh(db: Session):
    with APIFootballClient() as client:
        sync_teams(db, client)
        sync_upcoming_fixtures(db, client)
        sync_finished_results(db, client)
    from app.services.predictor import generate_predictions_for_upcoming
    generate_predictions_for_upcoming(db)


@router.post("/refresh")
def trigger_refresh(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Manually trigger a full data refresh + prediction run."""
    background_tasks.add_task(_full_refresh, db)
    return {"status": "refresh started in background"}


@router.post("/ingest-statsbomb")
def trigger_statsbomb_ingest(background_tasks: BackgroundTasks, db: Session = Depends(get_db)):
    """Trigger a one-time StatsBomb historical data download for ML training."""
    background_tasks.add_task(ingest_statsbomb_history, db)
    return {"status": "StatsBomb ingestion started in background"}
