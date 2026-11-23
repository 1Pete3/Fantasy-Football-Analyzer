from socket import timeout
from time import perf_counter
import requests
from dotenv import load_dotenv
import os
from rich import print_json
from requests_cache import CachedSession, SQLiteCache
import logging
from rich.logging import RichHandler
from datetime import datetime
import uuid

BASE_URL = "https://api.sleeper.app/v1"
TIMEOUT = 10

logger = logging.getLogger(__name__)

backend = SQLiteCache("cache/http_cache.sqlite", timeout=30)
session = CachedSession("http_cache", backend=backend)


class SleeperNotFoundError(Exception):
    """Sleeper returned an empty (null) response for a resource."""


def _get(path: str):
    """GET a Sleeper endpoint and return parsed JSON"""
    response = session.get(f"{BASE_URL}{path}", timeout=TIMEOUT)
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
    return _get(f"/players/nfl")


# --- main ---
def main():
    run_id = uuid.uuid4()
    today = datetime.now().strftime("%Y-%m-%d")
    start = perf_counter()
    log_path = f"logs/{today}_league_data.log"
    run_status = "error"

    if not os.path.exists("logs"):
        os.mkdir("logs")

    logging.basicConfig(
        filename=log_path,
        filemode="a",
        level="DEBUG",
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
    )
    logging.getLogger("requests_cache").setLevel(logging.WARNING)

    try:
        logger.info("===== RUN START: run_id=%s =====", run_id)
        load_dotenv()
        league_id = os.getenv("SLEEPER_LEAGUE_ID")

        if not league_id:
            raise SystemExit("SLEEPER_LEAGUE_ID is not set in .env")

        league = get_league(league_id)
        # print_json(data=league["roster_positions"])

        rosters = get_rosters(league_id)
        # print_json(data=rosters)

        users = get_users_in_league(league_id)
        # print_json(data=users)

        matchups = get_matchups(league_id, week=1)
        # print_json(data=matchups)

        transactions = get_transactions(league_id, 1)
        # print_json(data=transactions)

        state = get_nfl_state()
        # print_json(data=state)

        player = get_all_players("QB", True)
        # print_json(player)
        run_status = "success"
    except Exception:
        logger.exception("Main failed to run")
        raise
    finally:
        end = perf_counter()
        runtime = end - start
        logger.info(
            "===== RUN END: run_id=%s duration=%s status=%s =====",
            run_id,
            str(round(runtime, 2)),
            run_status,
        )


if __name__ == "__main__":
    main()
