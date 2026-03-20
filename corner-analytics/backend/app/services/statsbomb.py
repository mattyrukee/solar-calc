"""
StatsBomb Open Data fetcher.

Pulls free historical match + corner data from the StatsBomb open-data GitHub repo:
  https://github.com/statsbomb/open-data

Data is downloaded on-demand and cached locally under data/statsbomb/.
"""
import json
import logging
import os
from pathlib import Path
from typing import Any

import httpx

log = logging.getLogger(__name__)

# Raw GitHub base URL for StatsBomb open-data
_BASE = "https://raw.githubusercontent.com/statsbomb/open-data/master/data"

# Local cache directory (mounted as a volume in Docker)
_CACHE_DIR = Path(os.getenv("STATSBOMB_CACHE_DIR", "data/statsbomb"))

# StatsBomb competition IDs that map to our supported leagues
SUPPORTED_COMPETITIONS = {
    2: "Premier League",     # competition_id 2
    11: "La Liga",           # competition_id 11
    9: "Bundesliga",         # competition_id 9 (note: limited coverage in open data)
    12: "Serie A",           # competition_id 12 (note: limited coverage in open data)
}


def _cache_path(relative: str) -> Path:
    path = _CACHE_DIR / relative
    path.parent.mkdir(parents=True, exist_ok=True)
    return path


def _fetch(url: str, cache_file: str, force_refresh: bool = False) -> Any:
    """Fetch JSON from URL, using local file cache."""
    path = _cache_path(cache_file)
    if path.exists() and not force_refresh:
        with open(path) as f:
            return json.load(f)

    log.info("Fetching %s", url)
    response = httpx.get(url, timeout=30)
    response.raise_for_status()
    data = response.json()

    with open(path, "w") as f:
        json.dump(data, f)

    return data


def fetch_competitions() -> list[dict]:
    """Return all StatsBomb open-data competitions."""
    return _fetch(f"{_BASE}/competitions.json", "competitions.json")


def fetch_matches(competition_id: int, season_id: int) -> list[dict]:
    """Return all matches for a given competition + season."""
    url = f"{_BASE}/matches/{competition_id}/{season_id}.json"
    cache = f"matches/{competition_id}/{season_id}.json"
    return _fetch(url, cache)


def fetch_events(match_id: int) -> list[dict]:
    """Return all events for a given match."""
    url = f"{_BASE}/events/{match_id}.json"
    cache = f"events/{match_id}.json"
    return _fetch(url, cache)


def count_corners_from_events(events: list[dict]) -> dict[str, int]:
    """
    Count corners taken by each team from a StatsBomb event list.

    StatsBomb encodes corners as Pass events with pass.type.name == 'Corner'.
    Returns: {"home": n, "away": n}
    """
    home_corners = 0
    away_corners = 0

    for event in events:
        if event.get("type", {}).get("name") != "Pass":
            continue
        pass_data = event.get("pass", {})
        if pass_data.get("type", {}).get("name") != "Corner":
            continue

        team_name = event.get("team", {}).get("name", "")
        # StatsBomb marks home/away via index position in the lineup, but
        # we track it via the match's home_team field set by the caller.
        if event.get("index"):  # truthy check — just accumulate by team name
            pass

        # We resolve home/away by the caller providing home_team_name
        if "home_team_name" in event:  # sentinel added by our ingestion wrapper
            home_corners += 1
        else:
            away_corners += 1

    return {"home": home_corners, "away": away_corners}


def extract_match_corners(match_id: int, home_team_name: str) -> dict[str, int]:
    """
    Fetch events for a match and count corners per side.

    Returns {"home": int, "away": int, "total": int}
    """
    try:
        events = fetch_events(match_id)
    except httpx.HTTPStatusError as e:
        log.warning("Could not fetch events for match %d: %s", match_id, e)
        return {"home": 0, "away": 0, "total": 0}

    home_c = 0
    away_c = 0

    for event in events:
        if event.get("type", {}).get("name") != "Pass":
            continue
        pass_data = event.get("pass", {})
        if pass_data.get("type", {}).get("name") != "Corner":
            continue

        team_name = event.get("team", {}).get("name", "")
        if team_name == home_team_name:
            home_c += 1
        else:
            away_c += 1

    return {"home": home_c, "away": away_c, "total": home_c + away_c}


def get_available_seasons(competition_id: int) -> list[dict]:
    """Return seasons available for a competition in the open data."""
    competitions = fetch_competitions()
    return [
        c for c in competitions
        if c.get("competition_id") == competition_id
    ]


def iter_historical_matches(competition_id: int, max_seasons: int = 3) -> list[dict]:
    """
    Yield enriched match dicts for up to `max_seasons` seasons of a competition.

    Each dict contains match metadata + corner counts extracted from events.
    """
    seasons = get_available_seasons(competition_id)
    # Most recent seasons first
    seasons = sorted(seasons, key=lambda s: s.get("season_id", 0), reverse=True)
    enriched = []

    for season in seasons[:max_seasons]:
        season_id = season["season_id"]
        season_name = season.get("season_name", str(season_id))
        log.info(
            "Processing competition=%d season=%s (%d)",
            competition_id, season_name, season_id,
        )
        try:
            matches = fetch_matches(competition_id, season_id)
        except httpx.HTTPStatusError:
            log.warning("No match data for competition=%d season=%d", competition_id, season_id)
            continue

        for match in matches:
            home_team = match.get("home_team", {}).get("home_team_name", "")
            corners = extract_match_corners(match["match_id"], home_team)
            enriched.append(
                {
                    "match_id": match["match_id"],
                    "match_date": match.get("match_date"),
                    "competition_id": competition_id,
                    "season_id": season_id,
                    "season_name": season_name,
                    "home_team": home_team,
                    "away_team": match.get("away_team", {}).get("away_team_name", ""),
                    "home_score": match.get("home_score"),
                    "away_score": match.get("away_score"),
                    "home_corners": corners["home"],
                    "away_corners": corners["away"],
                    "total_corners": corners["total"],
                    # Shooting / possession stats (not always present in open data)
                    "home_possession": None,
                    "away_possession": None,
                }
            )

    return enriched
