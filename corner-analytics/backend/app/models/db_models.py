from datetime import datetime
from sqlalchemy import (
    Column, Integer, String, Float, DateTime, ForeignKey,
    Boolean, Enum as SAEnum, UniqueConstraint
)
from sqlalchemy.orm import relationship, declarative_base
import enum

Base = declarative_base()


class MatchStatus(str, enum.Enum):
    scheduled = "scheduled"
    live = "live"
    finished = "finished"
    postponed = "postponed"


class League(Base):
    __tablename__ = "leagues"

    id = Column(Integer, primary_key=True)
    api_id = Column(Integer, unique=True, nullable=False)  # API-Football league id
    name = Column(String(100), nullable=False)
    short_name = Column(String(20), nullable=False)        # "PL", "LL", "BL", "SA"
    country = Column(String(50), nullable=False)
    logo_url = Column(String(255))

    teams = relationship("Team", back_populates="league")
    matches = relationship("Match", back_populates="league")


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True)
    api_id = Column(Integer, unique=True, nullable=False)  # API-Football team id
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False)
    name = Column(String(100), nullable=False)
    short_name = Column(String(30))
    logo_url = Column(String(255))

    league = relationship("League", back_populates="teams")
    home_matches = relationship("Match", foreign_keys="Match.home_team_id", back_populates="home_team")
    away_matches = relationship("Match", foreign_keys="Match.away_team_id", back_populates="away_team")
    stats = relationship("TeamMatchStats", back_populates="team")


class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True)
    api_id = Column(Integer, unique=True, nullable=False)  # API-Football fixture id
    league_id = Column(Integer, ForeignKey("leagues.id"), nullable=False)
    season = Column(Integer, nullable=False)               # e.g. 2024
    fixture_date = Column(DateTime, nullable=False)
    home_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    away_team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    status = Column(SAEnum(MatchStatus), default=MatchStatus.scheduled)

    # Result (populated after match finishes)
    home_score = Column(Integer)
    away_score = Column(Integer)
    home_corners = Column(Integer)
    away_corners = Column(Integer)
    total_corners = Column(Integer)

    # Match context flags
    is_derby = Column(Boolean, default=False)
    is_title_decider = Column(Boolean, default=False)
    is_relegation = Column(Boolean, default=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    league = relationship("League", back_populates="matches")
    home_team = relationship("Team", foreign_keys=[home_team_id], back_populates="home_matches")
    away_team = relationship("Team", foreign_keys=[away_team_id], back_populates="away_matches")
    home_stats = relationship("TeamMatchStats", foreign_keys="TeamMatchStats.match_id",
                              primaryjoin="and_(Match.id==TeamMatchStats.match_id, TeamMatchStats.is_home==True)",
                              viewonly=True)
    away_stats = relationship("TeamMatchStats", foreign_keys="TeamMatchStats.match_id",
                              primaryjoin="and_(Match.id==TeamMatchStats.match_id, TeamMatchStats.is_home==False)",
                              viewonly=True)
    prediction = relationship("Prediction", back_populates="match", uselist=False)


class TeamMatchStats(Base):
    """Per-team, per-match stats used for feature engineering."""
    __tablename__ = "team_match_stats"
    __table_args__ = (
        UniqueConstraint("match_id", "team_id", name="uq_match_team"),
    )

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    is_home = Column(Boolean, nullable=False)

    # Corner stats
    corners_for = Column(Integer)
    corners_against = Column(Integer)

    # Attacking stats (from API-Football or StatsBomb)
    shots_total = Column(Integer)
    shots_on_target = Column(Integer)
    possession = Column(Float)       # 0–100 %

    # Pressing proxy (PPDA — lower = more intense press)
    ppda = Column(Float)

    # Formation (e.g. "4-3-3")
    formation = Column(String(20))

    team = relationship("Team", back_populates="stats")


class Prediction(Base):
    __tablename__ = "predictions"

    id = Column(Integer, primary_key=True)
    match_id = Column(Integer, ForeignKey("matches.id"), unique=True, nullable=False)

    # Core prediction output
    predicted_total = Column(Float, nullable=False)   # e.g. 10.4
    low_bound = Column(Integer, nullable=False)        # 5th percentile
    high_bound = Column(Integer, nullable=False)       # 95th percentile
    confidence_score = Column(Float, nullable=False)   # 0.0 – 1.0

    # Feature snapshot stored for explainability
    home_avg_corners_for = Column(Float)
    away_avg_corners_for = Column(Float)
    home_avg_corners_against = Column(Float)
    away_avg_corners_against = Column(Float)
    h2h_avg_corners = Column(Float)
    home_press_intensity = Column(Float)
    away_press_intensity = Column(Float)
    league_avg_corners = Column(Float)

    model_version = Column(String(20), nullable=False)
    generated_at = Column(DateTime, default=datetime.utcnow)

    match = relationship("Match", back_populates="prediction")
