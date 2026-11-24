import logging
from pathlib import Path

from requests_cache import DO_NOT_CACHE, CachedSession, SQLiteCache

BASE_URL = "https://api.sleeper.app/v1"
TIMEOUT = 10

URLS_EXPIRE_AFTER = {
    f"{BASE_URL}/players/nfl": 86400,
}

logger = logging.getLogger(__name__)

# src/fantasy_football_analyzer/sleeper.py -> project root
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CACHE_DIR = PROJECT_ROOT / "cache"
CACHE_DIR.mkdir(exist_ok=True)

backend = SQLiteCache(CACHE_DIR / "http_cache.sqlite", timeout=30)
session = CachedSession(
    "http_cache",
    backend=backend,
    urls_expire_after=URLS_EXPIRE_AFTER,
    expire_after=DO_NOT_CACHE,
)


class SleeperNotFoundError(Exception):
    """Sleeper returned an empty (null) response for a resource."""


def _get(path: str):
    """GET a Sleeper endpoint and return parsed JSON"""
    response = session.get(f"{BASE_URL}{path}", timeout=TIMEOUT)
    logger.debug("path=%s, from_cache=%s", path, response.from_cache)
    response.raise_for_status()
    data = response.json()
    if data is None:
        raise SleeperNotFoundError(f"Nothing found at {path}")
    return data


def _validate_week(week: int) -> None:
    if not 1 <= week <= 18:
        raise ValueError("Week must be between 1 and 18")


# --- League endpoints ---
def get_league(
    league_id: str,
) -> dict:
    """Return league info: settings, scoring_settings, roster_positions."""
    return _get(f"/league/{league_id}")


def get_rosters(league_id: str) -> list[dict]:
    """Return roster info of users in league: starters, wins, losses, points for, points against, players on team."""
    return _get(f"/league/{league_id}/rosters")


def get_users_in_league(league_id: str) -> list[dict]:
    """Return user info of users in the league: user id, username, display name, team name."""
    return _get(f"/league/{league_id}/users")


def get_matchups(league_id: str, week: int) -> list[dict]:
    """Return match up info for a specific week: starters, players, points. A matching matchup_id means two teams are facing each other."""
    _validate_week(week)
    return _get(f"/league/{league_id}/matchups/{week}")


def get_transactions(league_id: str, week: int) -> list[dict]:
    """Return all free agent transactions, waivers and trades: week is the week you want to pull from."""
    _validate_week(week)
    return _get(f"/league/{league_id}/transactions/{week}")


def get_nfl_state() -> dict:
    """Return info about current state for the NFL."""
    return _get("/state/nfl")


# --- Draft API Information ---
def get_all_drafts(league_id: str) -> list[dict]:
    """Return all drafts for a league: Sorted by most recent to earliest."""
    return _get(f"/league/{league_id}/drafts")


def get_specific_draft(draft_id: str) -> dict:
    """Return a specific draft for a league."""
    return _get(f"/draft/{draft_id}")


def get_all_picks_in_draft(draft_id: str) -> list[dict]:
    """Return all picks in a draft."""
    return _get(f"/draft/{draft_id}/picks")


# --- Player API Information ---
def get_all_players(position: str | None = None, active: bool | None = None):
    return _get("/players/nfl")
