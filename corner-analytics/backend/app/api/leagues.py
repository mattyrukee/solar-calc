from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.db_models import League
from app.models.schemas import LeagueOut

router = APIRouter()


@router.get("/", response_model=list[LeagueOut])
def list_leagues(db: Session = Depends(get_db)):
    return db.query(League).all()
