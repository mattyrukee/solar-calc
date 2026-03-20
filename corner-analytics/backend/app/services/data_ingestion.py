"""
Main data ingestion service.

Orchestrates two data sources:
  1. StatsBomb Open Data — historical matches used to train the ML model
  2. API-Football (free tier) — upcoming fixtures + recent results for live use

Typical nightly run order:
  1. sync_teams()              — ensure all teams exist in DB
  2. sync_upcoming_fixtures()  — pull next 7 days of scheduled matches
  3. sync_finished_results()   — update corners/scores for recently finished matches
  4. sync_team_stats()         — recompute rolling TeamMatchStats for all active teams
"""
import logging
from datetime import date, timedelta
from typing import Optional

from sqlalchemy.orm import Session

from app.models.db_models import League, Match, MatchStatus, Team, TeamMatchStats
from app.services.api_football import APIFootballClient, CURRENT_SEASON
from app.services import statsbomb

log = logging.getLogger(__name__)


# --------------------------------------------------------------------------- #
# Teams                                                                        #
# --------------------------------------------------------------------------- #

def sync_teams(db: Session, client: APIFootballClient) -> None:
    """Fetch and upsert all teams for each supported league."""
    leagues = db.query(League).all()
    for league in leagues:
        try:
            raw_teams = client.fetch_teams(league.api_id)
        except Exception as exc:
            log.error("Failed to fetch teams for league %s: %s", league.short_name, exc)
            continue

        for item in raw_teams:
            team_data = item.get("team", {})
            api_id = team_data.get("id")
            if not api_id:
                continue

            team = db.query(Team).filter(Team.api_id == api_id).first()
            if team is None:
                team = Team(
                    api_id=api_id,
                    league_id=league.id,
                    name=team_data.get("name", "Unknown"),
                    short_name=team_data.get("code"),
                    logo_url=team_data.get("logo"),
                )
                db.add(team)
                log.info("Added team: %s", team.name)
            else:
                team.logo_url = team_data.get("logo", team.logo_url)

    db.commit()
    log.info("Teams sync complete.")


# --------------------------------------------------------------------------- #
# Upcoming fixtures                                                            #
# --------------------------------------------------------------------------- #

def sync_upcoming_fixtures(
    db: Session,
    client: APIFootballClient,
    days_ahead: int = 7,
    season: int = CURRENT_SEASON,
) -> None:
    """Fetch and upsert scheduled fixtures for the next N days across all leagues."""
    from_date = date.today()
    to_date = from_date + timedelta(days=days_ahead)
    leagues = db.query(League).all()

    for league in leagues:
        try:
            fixtures = client.fetch_upcoming_fixtures(
                league.api_id, from_date, to_date, season
            )
        except Exception as exc:
            log.error("Failed to fetch fixtures for %s: %s", league.short_name, exc)
            continue

        for item in fixtures:
            _upsert_fixture(db, item, league, MatchStatus.scheduled)

    db.commit()
    log.info("Upcoming fixtures sync complete.")


# --------------------------------------------------------------------------- #
# Finished results + corner stats                                              #
# --------------------------------------------------------------------------- #

def sync_finished_results(
    db: Session,
    client: APIFootballClient,
    days_back: int = 3,
    season: int = CURRENT_SEASON,
) -> None:
    """
    Pull recently finished matches and update corner / score data.
    Also populates TeamMatchStats rows for the feature engine to consume.
    """
    from_date = date.today() - timedelta(days=days_back)
    to_date = date.today()
    leagues = db.query(League).all()

    for league in leagues:
        try:
            finished = client.fetch_finished_fixtures(
                league.api_id, from_date, to_date, season
            )
        except Exception as exc:
            log.error("Failed to fetch results for %s: %s", league.short_name, exc)
            continue

        for item in finished:
            match = _upsert_fixture(db, item, league, MatchStatus.finished)
            if match is None:
                continue

            # Fetch per-team statistics (corners, shots, possession)
            fixture_api_id = item.get("fixture", {}).get("id")
            try:
                stats_raw = client.fetch_match_statistics(fixture_api_id)
            except Exception as exc:
                log.warning("No stats for fixture %d: %s", fixture_api_id, exc)
                continue

            corners = client.parse_corners(stats_raw)
            possession = client.parse_possession(stats_raw)
            shots = client.parse_shots(stats_raw)

            match.home_corners = corners["home"]
            match.away_corners = corners["away"]
            match.total_corners = corners["total"]
            match.status = MatchStatus.finished

            _upsert_team_stats(
                db, match,
                is_home=True,
                corners_for=corners["home"],
                corners_against=corners["away"],
                shots_total=shots["home"]["total"],
                shots_on_target=shots["home"]["on_target"],
                possession=possession["home"],
            )
            _upsert_team_stats(
                db, match,
                is_home=False,
                corners_for=corners["away"],
                corners_against=corners["home"],
                shots_total=shots["away"]["total"],
                shots_on_target=shots["away"]["on_target"],
                possession=possession["away"],
            )

    db.commit()
    log.info("Finished results sync complete.")


# --------------------------------------------------------------------------- #
# StatsBomb historical ingestion (run once for model training data)            #
# --------------------------------------------------------------------------- #

def ingest_statsbomb_history(db: Session, max_seasons_per_competition: int = 3) -> None:
    """
    Ingest historical match + corner data from StatsBomb Open Data.

    This is intended to be run once (or infrequently) to build up the
    training dataset. It stores results in `team_match_stats` so the
    feature engine can calculate rolling averages.

    Note: StatsBomb open data uses its own team names which won't always
    match API-Football names. We store them in a separate raw cache and
    the ML training pipeline reads directly from StatsBomb files, not the DB.
    """
    for competition_id, competition_name in statsbomb.SUPPORTED_COMPETITIONS.items():
        log.info("Ingesting StatsBomb data for %s (competition_id=%d)", competition_name, competition_id)
        try:
            matches = statsbomb.iter_historical_matches(
                competition_id, max_seasons=max_seasons_per_competition
            )
        except Exception as exc:
            log.error("StatsBomb ingestion failed for competition %d: %s", competition_id, exc)
            continue

        log.info(
            "Fetched %d historical matches for %s from StatsBomb",
            len(matches), competition_name,
        )
        # The raw enriched match dicts are saved to disk by the StatsBomb
        # service. The ML training pipeline reads them from cache.
        # No DB writes needed here — keeping training data separate
        # avoids polluting live match records with name-mismatched teams.

    log.info("StatsBomb historical ingestion complete.")


# --------------------------------------------------------------------------- #
# Internal helpers                                                             #
# --------------------------------------------------------------------------- #

def _upsert_fixture(
    db: Session,
    item: dict,
    league: League,
    status: MatchStatus,
) -> Optional[Match]:
    """Insert or update a single fixture from an API-Football response item."""
    fixture_data = item.get("fixture", {})
    api_id = fixture_data.get("id")
    if not api_id:
        return None

    home_data = item.get("teams", {}).get("home", {})
    away_data = item.get("teams", {}).get("away", {})

    home_team = db.query(Team).filter(Team.api_id == home_data.get("id")).first()
    away_team = db.query(Team).filter(Team.api_id == away_data.get("id")).first()

    if home_team is None or away_team is None:
        # Teams not yet in DB — skip and let sync_teams handle it
        log.debug("Skipping fixture %d — teams not yet synced", api_id)
        return None

    from datetime import datetime
    fixture_date_str = fixture_data.get("date", "")
    try:
        fixture_date = datetime.fromisoformat(fixture_date_str.replace("Z", "+00:00"))
    except (ValueError, AttributeError):
        log.warning("Cannot parse fixture date '%s', skipping fixture %d", fixture_date_str, api_id)
        return None

    league_season = item.get("league", {}).get("season", CURRENT_SEASON)

    match = db.query(Match).filter(Match.api_id == api_id).first()
    if match is None:
        match = Match(
            api_id=api_id,
            league_id=league.id,
            season=league_season,
            fixture_date=fixture_date,
            home_team_id=home_team.id,
            away_team_id=away_team.id,
            status=status,
        )
        db.add(match)
        log.info("Added fixture: %s vs %s on %s", home_team.name, away_team.name, fixture_date.date())
    else:
        match.status = status
        match.fixture_date = fixture_date

    # Update score if available
    goals = item.get("goals", {})
    if goals.get("home") is not None:
        match.home_score = goals["home"]
        match.away_score = goals["away"]

    return match


def _upsert_team_stats(
    db: Session,
    match: Match,
    is_home: bool,
    corners_for: int,
    corners_against: int,
    shots_total: int,
    shots_on_target: int,
    possession: float,
    ppda: Optional[float] = None,
) -> None:
    """Insert or update a TeamMatchStats row."""
    team_id = match.home_team_id if is_home else match.away_team_id

    stats = (
        db.query(TeamMatchStats)
        .filter(TeamMatchStats.match_id == match.id, TeamMatchStats.team_id == team_id)
        .first()
    )
    if stats is None:
        stats = TeamMatchStats(match_id=match.id, team_id=team_id, is_home=is_home)
        db.add(stats)

    stats.corners_for = corners_for
    stats.corners_against = corners_against
    stats.shots_total = shots_total
    stats.shots_on_target = shots_on_target
    stats.possession = possession
    stats.ppda = ppda
