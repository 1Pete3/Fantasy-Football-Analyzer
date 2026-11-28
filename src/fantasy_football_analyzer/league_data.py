import logging
from typing import Any

from fantasy_football_analyzer.models import Roster, User
from fantasy_football_analyzer.sleeper import (
    get_all_players,
    get_rosters,
    get_users_in_league,
)

logger = logging.getLogger(__name__)


def format_player(player_id, first_name, last_name, postion) -> dict[Any, Any]:
    player = {}
    player[player_id] = {
        "first_name": first_name,
        "last_name": last_name,
        "position": postion,
    }
    return player


def get_player_info(player_list, all_players) -> list[Any]:
    formatted_player_list = []
    for player in player_list or []:
        if player != "0":
            player_info = all_players.get(player) or {}
            if not player_info:
                logger.warning("Unknown player id %s", player)
            formatted_player_list.append(
                format_player(
                    player,
                    player_info.get("first_name") or "",
                    player_info.get("last_name") or "",
                    player_info.get("position") or "",
                )
            )
    return formatted_player_list


def format_fantasy_points(int_points, decimal_points) -> Any:
    points = int_points + (decimal_points / 100)
    return points


def get_member_info(league_id:str) -> dict[Any, Any]:
    all_players = get_all_players()
    users: list[dict[Any, Any]] = get_users_in_league(league_id)
    rosters: list[dict[Any, Any]] = get_rosters(league_id)

    users_by_id = {}
    for user in users:
        users_by_id[user["user_id"]] = User(
            user_id=user["user_id"],
            display_name=user["display_name"],
            league_id=user["league_id"],
            team_name=(user.get("metadata") or {}).get("team_name")
            or user["display_name"],
        )

    member = {}
    for roster in rosters:
        member[roster["roster_id"]] = {
            "user": users_by_id.get(roster["owner_id"]),
            "roster": {},
        }
        member[roster["roster_id"]]["roster"] = Roster(
            user_id=roster["owner_id"],
            co_owners=roster.get("co_owners", None),
            league_id=roster.get("league_id"),
            points_for=format_fantasy_points(
                (roster.get("settings") or {}).get("fpts", 0),
                (roster.get("settings") or {}).get("fpts_decimal", 0),
            ),
            points_against=format_fantasy_points(
                (roster.get("settings") or {}).get("fpts_against", 0),
                (roster.get("settings") or {}).get("fpts_against_decimal", 0),
            ),
            wins=(roster.get("settings") or {}).get("wins", 0),
            losses=(roster.get("settings") or {}).get("losses", 0),
            ties=(roster.get("settings") or {}).get("ties", 0),
            roster_id=roster.get("roster_id"),
            players=get_player_info(roster.get("players"), all_players),
            starters=get_player_info(roster.get("starters"), all_players),
            record=(roster.get("metadata") or {}).get("record", None),
            streak=(roster.get("metadata") or {}).get("streak", None),
        )

    return member
