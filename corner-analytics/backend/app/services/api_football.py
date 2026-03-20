"""
API-Football (RapidAPI) client — free tier.

Free tier limits: 100 requests/day.
We budget them carefully:
  - 4 leagues × 1 req/day for upcoming fixtures  = 4 req
  - ~10 finished matches/day × 1 req each stats  = 10 req (worst case)
  - Leaves headroom for retries and manual refresh

Docs: https://www.api-football.com/documentation-v3
"""
import logging
from datetime import date, timedelta
from typing import Any, Optional

import httpx

from app.config import settings

log = logging.getLogger(__name__)

_BASE_URL = "https://v3.football.api-sports.io"

# API-Football IDs for our supported leagues
LEAGUE_IDS = {
    "PL": 39,    # Premier League
    "LL": 140,   # La Liga
    "BL": 78,    # Bundesliga
    "SA": 135,   # Serie A
}

# Current season (used when no season is specified)
CURRENT_SEASON = 2024


class APIFootballClient:
    def __init__(self):
        self._headers = {
            "x-rapidapi-key": settings.API_FOOTBALL_KEY,
            "x-rapidapi-host": settings.API_FOOTBALL_HOST,
        }
        self._client = httpx.Client(
            base_url=_BASE_URL,
            headers=self._headers,
            timeout=15,
        )

    def _get(self, path: str, params: dict) -> Any:
        log.info("API-Football GET %s params=%s", path, params)
        response = self._client.get(path, params=params)
        response.raise_for_status()
        data = response.json()
        errors = data.get("errors", {})
        if errors:
            raise RuntimeError(f"API-Football error: {errors}")
        return data.get("response", [])

    # ------------------------------------------------------------------ #
    # Teams                                                                #
    # ------------------------------------------------------------------ #

    def fetch_teams(self, league_id: int, season: int = CURRENT_SEASON) -> list[dict]:
        """Return all teams for a league/season."""
        return self._get("/teams", {"league": league_id, "season": season})

    # ------------------------------------------------------------------ #
    # Fixtures                                                             #
    # ------------------------------------------------------------------ #

    def fetch_upcoming_fixtures(
        self,
        league_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        season: int = CURRENT_SEASON,
    ) -> list[dict]:
        """Return scheduled fixtures for the next N days."""
        from_date = from_date or date.today()
        to_date = to_date or (from_date + timedelta(days=7))
        return self._get(
            "/fixtures",
            {
                "league": league_id,
                "season": season,
                "from": from_date.isoformat(),
                "to": to_date.isoformat(),
                "status": "NS",  # Not Started
            },
        )

    def fetch_finished_fixtures(
        self,
        league_id: int,
        from_date: Optional[date] = None,
        to_date: Optional[date] = None,
        season: int = CURRENT_SEASON,
    ) -> list[dict]:
        """Return finished fixtures to back-fill results."""
        from_date = from_date or (date.today() - timedelta(days=2))
        to_date = to_date or date.today()
        return self._get(
            "/fixtures",
            {
                "league": league_id,
                "season": season,
                "from": from_date.isoformat(),
                "to": to_date.isoformat(),
                "status": "FT",  # Full Time
            },
        )

    # ------------------------------------------------------------------ #
    # Match statistics (corners, shots, possession, etc.)                  #
    # ------------------------------------------------------------------ #

    def fetch_match_statistics(self, fixture_id: int) -> list[dict]:
        """
        Return per-team statistics for a finished fixture.

        Each item in the list is a team's stats block:
        {
          "team": {"id": 33, "name": "Manchester United", ...},
          "statistics": [
            {"type": "Corner Kicks", "value": 6},
            {"type": "Ball Possession", "value": "52%"},
            {"type": "Total Shots", "value": 12},
            ...
          ]
        }
        """
        return self._get("/fixtures/statistics", {"fixture": fixture_id})

    # ------------------------------------------------------------------ #
    # Helpers                                                              #
    # ------------------------------------------------------------------ #

    def parse_corners(self, stats_response: list[dict]) -> dict[str, int]:
        """
        Extract corner counts from fetch_match_statistics() output.

        Returns {"home": int, "away": int, "total": int}
        """
        corners = []
        for team_block in stats_response:
            for stat in team_block.get("statistics", []):
                if stat.get("type") == "Corner Kicks":
                    val = stat.get("value") or 0
                    corners.append(int(val))

        if len(corners) == 2:
            return {"home": corners[0], "away": corners[1], "total": sum(corners)}
        return {"home": 0, "away": 0, "total": 0}

    def parse_possession(self, stats_response: list[dict]) -> dict[str, float]:
        """Return {"home": float, "away": float} possession percentages."""
        possession = []
        for team_block in stats_response:
            for stat in team_block.get("statistics", []):
                if stat.get("type") == "Ball Possession":
                    raw = stat.get("value") or "0%"
                    possession.append(float(str(raw).replace("%", "")))
        if len(possession) == 2:
            return {"home": possession[0], "away": possession[1]}
        return {"home": 0.0, "away": 0.0}

    def parse_shots(self, stats_response: list[dict]) -> dict[str, dict]:
        """Return {"home": {"total": int, "on_target": int}, "away": {...}}."""
        result = []
        for team_block in stats_response:
            shots_total = 0
            shots_on = 0
            for stat in team_block.get("statistics", []):
                if stat.get("type") == "Total Shots":
                    shots_total = int(stat.get("value") or 0)
                if stat.get("type") == "Shots on Goal":
                    shots_on = int(stat.get("value") or 0)
            result.append({"total": shots_total, "on_target": shots_on})
        if len(result) == 2:
            return {"home": result[0], "away": result[1]}
        return {"home": {"total": 0, "on_target": 0}, "away": {"total": 0, "on_target": 0}}

    def close(self):
        self._client.close()

    def __enter__(self):
        return self

    def __exit__(self, *_):
        self.close()
