from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.database import get_db
from app.models.db_models import Team, Match, TeamMatchStats
from app.models.schemas import TeamOut, TeamCornerHistory

router = APIRouter()


@router.get("/{team_id}", response_model=TeamOut)
def get_team(team_id: int, db: Session = Depends(get_db)):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")
    return team


@router.get("/{team_id}/corner-history", response_model=list[TeamCornerHistory])
def get_corner_history(
    team_id: int,
    last: int = Query(20, ge=5, le=50, description="Number of recent matches to return"),
    db: Session = Depends(get_db),
):
    team = db.query(Team).filter(Team.id == team_id).first()
    if not team:
        raise HTTPException(status_code=404, detail="Team not found")

    rows = (
        db.query(TeamMatchStats, Match)
        .join(Match, TeamMatchStats.match_id == Match.id)
        .filter(TeamMatchStats.team_id == team_id)
        .filter(Match.status == "finished")
        .order_by(desc(Match.fixture_date))
        .limit(last)
        .all()
    )

    history = []
    for stats, match in rows:
        is_home = stats.is_home
        opponent_id = match.away_team_id if is_home else match.home_team_id
        opponent = db.query(Team).filter(Team.id == opponent_id).first()
        history.append(
            TeamCornerHistory(
                match_id=match.id,
                fixture_date=match.fixture_date,
                opponent=opponent.name if opponent else "Unknown",
                is_home=is_home,
                corners_for=stats.corners_for,
                corners_against=stats.corners_against,
                total_corners=(stats.corners_for or 0) + (stats.corners_against or 0)
                if stats.corners_for is not None else None,
            )
        )
    return history
