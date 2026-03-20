from datetime import datetime
from typing import Optional
from pydantic import BaseModel


class LeagueOut(BaseModel):
    id: int
    name: str
    short_name: str
    country: str
    logo_url: Optional[str]

    model_config = {"from_attributes": True}


class TeamOut(BaseModel):
    id: int
    name: str
    short_name: Optional[str]
    logo_url: Optional[str]

    model_config = {"from_attributes": True}


class PredictionOut(BaseModel):
    predicted_total: float
    low_bound: int
    high_bound: int
    confidence_score: float
    home_avg_corners_for: Optional[float]
    away_avg_corners_for: Optional[float]
    h2h_avg_corners: Optional[float]
    league_avg_corners: Optional[float]
    model_version: str
    generated_at: datetime

    model_config = {"from_attributes": True}


class FixtureOut(BaseModel):
    id: int
    fixture_date: datetime
    league: LeagueOut
    home_team: TeamOut
    away_team: TeamOut
    status: str
    home_corners: Optional[int]
    away_corners: Optional[int]
    total_corners: Optional[int]
    prediction: Optional[PredictionOut]

    model_config = {"from_attributes": True}


class TeamCornerHistory(BaseModel):
    match_id: int
    fixture_date: datetime
    opponent: str
    is_home: bool
    corners_for: Optional[int]
    corners_against: Optional[int]
    total_corners: Optional[int]
