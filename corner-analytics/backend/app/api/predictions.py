from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.db_models import Match, Prediction
from app.models.schemas import PredictionOut, FixtureOut

router = APIRouter()


@router.get("/{fixture_id}", response_model=PredictionOut)
def get_prediction(fixture_id: int, db: Session = Depends(get_db)):
    match = db.query(Match).filter(Match.id == fixture_id).first()
    if not match:
        raise HTTPException(status_code=404, detail="Fixture not found")

    prediction = db.query(Prediction).filter(Prediction.match_id == fixture_id).first()
    if not prediction:
        raise HTTPException(status_code=404, detail="No prediction available for this fixture yet")

    return prediction
