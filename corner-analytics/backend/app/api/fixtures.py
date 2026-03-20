from datetime import date, datetime, timedelta
from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload
from app.database import get_db
from app.models.db_models import Match, MatchStatus
from app.models.schemas import FixtureOut

router = APIRouter()


@router.get("/", response_model=list[FixtureOut])
def list_fixtures(
    league_id: Optional[int] = Query(None, description="Filter by league id"),
    match_date: Optional[date] = Query(None, description="Filter by date (YYYY-MM-DD), defaults to today"),
    days_ahead: int = Query(7, ge=1, le=30, description="Days ahead to fetch if no date given"),
    db: Session = Depends(get_db),
):
    query = (
        db.query(Match)
        .options(
            joinedload(Match.home_team),
            joinedload(Match.away_team),
            joinedload(Match.league),
            joinedload(Match.prediction),
        )
        .filter(Match.status == MatchStatus.scheduled)
    )

    if league_id:
        query = query.filter(Match.league_id == league_id)

    if match_date:
        start = datetime.combine(match_date, datetime.min.time())
        end = start + timedelta(days=1)
    else:
        start = datetime.utcnow()
        end = start + timedelta(days=days_ahead)

    query = query.filter(Match.fixture_date >= start, Match.fixture_date < end)
    return query.order_by(Match.fixture_date).all()
