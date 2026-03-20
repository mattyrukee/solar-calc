"""
Feature engineering for the corner prediction model.

For every upcoming fixture we build a flat feature vector from:
  - Each team's rolling corner averages (home/away split, last 10 games)
  - Each team's rolling shot and possession averages
  - Head-to-head corner history
  - League season average corners
  - Match-context flags (derby, relegation, title)

All lookups use only matches BEFORE the fixture date to prevent data leakage.
"""
from __future__ import annotations

import logging
from dataclasses import dataclass, asdict
from datetime import datetime
from typing import Optional

from sqlalchemy import and_
from sqlalchemy.orm import Session

from app.models.db_models import Match, MatchStatus, Team, TeamMatchStats, League

log = logging.getLogger(__name__)

# Rolling window sizes
WINDOW_LONG = 10   # for averages
WINDOW_SHORT = 5   # for recent-form trend


@dataclass
class MatchFeatures:
    """Flat feature vector passed to the ML model."""
    # Home team corner averages (home games only)
    home_avg_corners_for_h: float
    home_avg_corners_against_h: float

    # Away team corner averages (away games only)
    away_avg_corners_for_a: float
    away_avg_corners_against_a: float

    # Overall averages (all venues, last WINDOW_LONG games)
    home_avg_corners_for_all: float
    away_avg_corners_for_all: float

    # Short-form corner trend (last WINDOW_SHORT games, all venues)
    home_form_corners: float
    away_form_corners: float

    # Attack intensity proxies
    home_avg_shots: float
    away_avg_shots: float
    home_avg_possession: float
    away_avg_possession: float

    # Head-to-head (last 5 H2H meetings)
    h2h_avg_total_corners: float
    h2h_matches_available: int

    # League baseline
    league_avg_corners: float

    # Match context (encoded as 0/1)
    is_derby: int
    is_title_decider: int
    is_relegation: int

    def to_dict(self) -> dict:
        return asdict(self)

    @property
    def feature_names(self) -> list[str]:
        return list(asdict(self).keys())


def build_features(
    db: Session,
    match: Match,
    cutoff_date: Optional[datetime] = None,
) -> Optional[MatchFeatures]:
    """
    Build a MatchFeatures vector for a single fixture.

    cutoff_date: only use match data before this date (for backtesting).
                 Defaults to match.fixture_date.
    Returns None if there is not enough historical data for either team.
    """
    cutoff = cutoff_date or match.fixture_date

    home_feats = _team_features(db, match.home_team_id, is_home=True, before=cutoff)
    away_feats = _team_features(db, match.away_team_id, is_home=False, before=cutoff)

    if home_feats is None or away_feats is None:
        log.debug("Not enough history for fixture %d — skipping", match.id)
        return None

    h2h_avg, h2h_count = _h2h_corners(
        db, match.home_team_id, match.away_team_id, before=cutoff
    )
    league_avg = _league_avg_corners(db, match.league_id, before=cutoff)

    return MatchFeatures(
        home_avg_corners_for_h=home_feats["avg_corners_for_home"],
        home_avg_corners_against_h=home_feats["avg_corners_against_home"],
        away_avg_corners_for_a=away_feats["avg_corners_for_away"],
        away_avg_corners_against_a=away_feats["avg_corners_against_away"],
        home_avg_corners_for_all=home_feats["avg_corners_for_all"],
        away_avg_corners_for_all=away_feats["avg_corners_for_all"],
        home_form_corners=home_feats["form_corners"],
        away_form_corners=away_feats["form_corners"],
        home_avg_shots=home_feats["avg_shots"],
        away_avg_shots=away_feats["avg_shots"],
        home_avg_possession=home_feats["avg_possession"],
        away_avg_possession=away_feats["avg_possession"],
        h2h_avg_total_corners=h2h_avg,
        h2h_matches_available=h2h_count,
        league_avg_corners=league_avg,
        is_derby=int(match.is_derby),
        is_title_decider=int(match.is_title_decider),
        is_relegation=int(match.is_relegation),
    )


# --------------------------------------------------------------------------- #
# Internal helpers                                                             #
# --------------------------------------------------------------------------- #

def _team_features(
    db: Session, team_id: int, is_home: bool, before: datetime
) -> Optional[dict]:
    """
    Compute per-team feature sub-dict from TeamMatchStats rows before cutoff.
    Returns None if the team has fewer than 3 finished matches.
    """
    # All finished matches for this team before the cutoff date
    all_stats = (
        db.query(TeamMatchStats, Match.fixture_date)
        .join(Match, TeamMatchStats.match_id == Match.id)
        .filter(
            TeamMatchStats.team_id == team_id,
            Match.status == MatchStatus.finished,
            Match.fixture_date < before,
            TeamMatchStats.corners_for.isnot(None),
        )
        .order_by(Match.fixture_date.desc())
        .limit(WINDOW_LONG)
        .all()
    )

    if len(all_stats) < 3:
        return None

    # Home-only stats (last WINDOW_LONG home games)
    home_stats = (
        db.query(TeamMatchStats)
        .join(Match, TeamMatchStats.match_id == Match.id)
        .filter(
            TeamMatchStats.team_id == team_id,
            TeamMatchStats.is_home == True,
            Match.status == MatchStatus.finished,
            Match.fixture_date < before,
            TeamMatchStats.corners_for.isnot(None),
        )
        .order_by(Match.fixture_date.desc())
        .limit(WINDOW_LONG)
        .all()
    )

    # Away-only stats
    away_stats = (
        db.query(TeamMatchStats)
        .join(Match, TeamMatchStats.match_id == Match.id)
        .filter(
            TeamMatchStats.team_id == team_id,
            TeamMatchStats.is_home == False,
            Match.status == MatchStatus.finished,
            Match.fixture_date < before,
            TeamMatchStats.corners_for.isnot(None),
        )
        .order_by(Match.fixture_date.desc())
        .limit(WINDOW_LONG)
        .all()
    )

    # Short-form: last WINDOW_SHORT all-venue games
    short_stats = [s for s, _ in all_stats[:WINDOW_SHORT]]

    def safe_mean(rows, attr: str, default=0.0) -> float:
        vals = [getattr(r, attr) for r in rows if getattr(r, attr) is not None]
        return sum(vals) / len(vals) if vals else default

    all_rows = [s for s, _ in all_stats]

    return {
        # Home-split
        "avg_corners_for_home": safe_mean(home_stats, "corners_for"),
        "avg_corners_against_home": safe_mean(home_stats, "corners_against"),
        # Away-split
        "avg_corners_for_away": safe_mean(away_stats, "corners_for"),
        "avg_corners_against_away": safe_mean(away_stats, "corners_against"),
        # All-venue
        "avg_corners_for_all": safe_mean(all_rows, "corners_for"),
        # Short form
        "form_corners": safe_mean(short_stats, "corners_for"),
        # Attack proxies
        "avg_shots": safe_mean(all_rows, "shots_total"),
        "avg_possession": safe_mean(all_rows, "possession"),
    }


def _h2h_corners(
    db: Session, home_team_id: int, away_team_id: int, before: datetime, limit: int = 5
) -> tuple[float, int]:
    """
    Return (avg_total_corners, number_of_h2h_matches) for the last `limit` H2H meetings.
    """
    matches = (
        db.query(Match)
        .filter(
            Match.status == MatchStatus.finished,
            Match.fixture_date < before,
            Match.total_corners.isnot(None),
            and_(
                Match.home_team_id.in_([home_team_id, away_team_id]),
                Match.away_team_id.in_([home_team_id, away_team_id]),
            ),
        )
        .order_by(Match.fixture_date.desc())
        .limit(limit)
        .all()
    )

    if not matches:
        return 0.0, 0

    avg = sum(m.total_corners for m in matches) / len(matches)
    return round(avg, 2), len(matches)


def _league_avg_corners(db: Session, league_id: int, before: datetime) -> float:
    """Season average total corners for the league up to cutoff date."""
    matches = (
        db.query(Match)
        .filter(
            Match.league_id == league_id,
            Match.status == MatchStatus.finished,
            Match.fixture_date < before,
            Match.total_corners.isnot(None),
        )
        .all()
    )

    if not matches:
        return 10.0  # sensible prior if no data yet

    return round(sum(m.total_corners for m in matches) / len(matches), 2)


# --------------------------------------------------------------------------- #
# Batch builder for training data                                              #
# --------------------------------------------------------------------------- #

def build_training_dataset(db: Session) -> tuple[list[dict], list[float]]:
    """
    Build the full training dataset from all finished matches in the DB.

    Returns (X_dicts, y_values) where:
      X_dicts: list of feature dicts
      y_values: list of actual total corner counts
    """
    finished = (
        db.query(Match)
        .filter(Match.status == MatchStatus.finished, Match.total_corners.isnot(None))
        .order_by(Match.fixture_date)
        .all()
    )

    X, y = [], []
    skipped = 0

    for match in finished:
        features = build_features(db, match, cutoff_date=match.fixture_date)
        if features is None:
            skipped += 1
            continue
        X.append(features.to_dict())
        y.append(float(match.total_corners))

    log.info(
        "Training dataset: %d samples built, %d skipped (insufficient history)",
        len(X), skipped,
    )
    return X, y
