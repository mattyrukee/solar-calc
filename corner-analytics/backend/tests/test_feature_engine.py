"""
Unit tests for the feature engine.

Uses an in-memory SQLite DB so no real PostgreSQL is needed.
"""
from datetime import datetime, timedelta

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models.db_models import Base, League, Team, Match, TeamMatchStats, MatchStatus
from app.services.feature_engine import (
    build_features,
    _h2h_corners,
    _league_avg_corners,
    WINDOW_LONG,
)


@pytest.fixture()
def db():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)
    Session = sessionmaker(bind=engine)
    session = Session()
    yield session
    session.close()


def _make_league(db) -> League:
    league = League(api_id=39, name="Premier League", short_name="PL", country="England")
    db.add(league)
    db.flush()
    return league


def _make_team(db, league, name, api_id) -> Team:
    team = Team(api_id=api_id, league_id=league.id, name=name, short_name=name[:3])
    db.add(team)
    db.flush()
    return team


def _make_finished_match(
    db, league, home, away, fixture_date, home_corners, away_corners
) -> Match:
    match = Match(
        api_id=abs(hash(f"{home.id}{away.id}{fixture_date}")),
        league_id=league.id,
        season=2024,
        fixture_date=fixture_date,
        home_team_id=home.id,
        away_team_id=away.id,
        status=MatchStatus.finished,
        home_corners=home_corners,
        away_corners=away_corners,
        total_corners=home_corners + away_corners,
        home_score=1,
        away_score=1,
    )
    db.add(match)
    db.flush()

    db.add(TeamMatchStats(
        match_id=match.id, team_id=home.id, is_home=True,
        corners_for=home_corners, corners_against=away_corners,
        shots_total=12, possession=52.0,
    ))
    db.add(TeamMatchStats(
        match_id=match.id, team_id=away.id, is_home=False,
        corners_for=away_corners, corners_against=home_corners,
        shots_total=9, possession=48.0,
    ))
    db.flush()
    return match


class TestLeagueAvgCorners:
    def test_returns_prior_when_no_data(self, db):
        league = _make_league(db)
        avg = _league_avg_corners(db, league.id, before=datetime.utcnow())
        assert avg == 10.0  # default prior

    def test_computes_correctly(self, db):
        league = _make_league(db)
        home = _make_team(db, league, "Arsenal", 1)
        away = _make_team(db, league, "Chelsea", 2)

        base = datetime(2024, 1, 1)
        _make_finished_match(db, league, home, away, base, 6, 4)    # 10 total
        _make_finished_match(db, league, away, home, base + timedelta(days=7), 5, 5)  # 10 total

        avg = _league_avg_corners(db, league.id, before=base + timedelta(days=30))
        assert avg == 10.0


class TestH2HCorners:
    def test_returns_zero_when_no_history(self, db):
        league = _make_league(db)
        home = _make_team(db, league, "Arsenal", 1)
        away = _make_team(db, league, "Chelsea", 2)
        avg, count = _h2h_corners(db, home.id, away.id, before=datetime.utcnow())
        assert avg == 0.0
        assert count == 0

    def test_averages_correctly(self, db):
        league = _make_league(db)
        home = _make_team(db, league, "Arsenal", 1)
        away = _make_team(db, league, "Chelsea", 2)

        base = datetime(2024, 1, 1)
        _make_finished_match(db, league, home, away, base, 7, 3)           # 10
        _make_finished_match(db, league, away, home, base + timedelta(7), 4, 6)  # 10
        _make_finished_match(db, league, home, away, base + timedelta(14), 5, 7)  # 12

        avg, count = _h2h_corners(db, home.id, away.id, before=base + timedelta(30))
        assert count == 3
        assert abs(avg - (10 + 10 + 12) / 3) < 0.01


class TestBuildFeatures:
    def test_returns_none_with_insufficient_history(self, db):
        league = _make_league(db)
        home = _make_team(db, league, "Arsenal", 1)
        away = _make_team(db, league, "Chelsea", 2)

        future_match = Match(
            api_id=9999,
            league_id=league.id,
            season=2024,
            fixture_date=datetime(2024, 8, 1),
            home_team_id=home.id,
            away_team_id=away.id,
            status=MatchStatus.scheduled,
        )
        db.add(future_match)
        db.flush()

        # No history — should return None
        result = build_features(db, future_match)
        assert result is None

    def test_builds_features_with_enough_history(self, db):
        league = _make_league(db)
        home = _make_team(db, league, "Arsenal", 1)
        away = _make_team(db, league, "Chelsea", 2)
        opponent = _make_team(db, league, "Liverpool", 3)

        base = datetime(2024, 1, 1)

        # Give each team 5+ finished matches
        for i in range(6):
            _make_finished_match(db, league, home, opponent, base + timedelta(days=i * 7), 6, 4)
            _make_finished_match(db, league, away, opponent, base + timedelta(days=i * 7 + 3), 5, 5)

        future_match = Match(
            api_id=9999,
            league_id=league.id,
            season=2024,
            fixture_date=base + timedelta(days=200),
            home_team_id=home.id,
            away_team_id=away.id,
            status=MatchStatus.scheduled,
        )
        db.add(future_match)
        db.flush()

        features = build_features(db, future_match)
        assert features is not None
        assert features.home_avg_corners_for_h > 0
        assert features.away_avg_corners_for_a > 0
        assert features.league_avg_corners > 0
        assert 0 <= features.is_derby <= 1
