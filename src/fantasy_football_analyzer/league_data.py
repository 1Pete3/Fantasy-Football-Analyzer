import os
from typing import Any

from dotenv import load_dotenv
from rich import print

from fantasy_football_analyzer.models import Roster, User
from fantasy_football_analyzer.sleeper import (
    get_all_players,
    get_rosters,
    get_users_in_league,
)

load_dotenv()

users: list[dict[Any, Any]] = get_users_in_league(os.getenv("SLEEPER_LEAGUE_ID"))
rosters: list[dict[Any, Any]] = get_rosters(os.getenv("SLEEPER_LEAGUE_ID"))
all_players = get_all_players()


def format_player(player_id, first_name, last_name, postion) -> dict[Any, Any]:
    player = {}
    player[player_id] = {
        "first_name": first_name,
        "last_name": last_name,
        "position": postion,
    }
    return player


def get_player_info(player_list) -> list[Any]:
    formatted_player_list = []
    for player in player_list:
        if player != "0":
            player_info = all_players.get(player)
            formatted_player_list.append(
                format_player(
                    player,
                    player_info.get("first_name", None),
                    player_info.get("last_name", ""),
                    player_info.get("position", ""),
                )
            )
    return formatted_player_list


def format_fantasy_points(int_points, decimal_points) -> Any:
    points = int_points + (decimal_points / 100)
    return points


def get_member_info() -> dict[Any, Any]:
    member = {}
    for roster in rosters:
        print(roster)
        member[roster["owner_id"]] = {"user": {}, "roster": {}}
        member[roster["owner_id"]]["roster"] = Roster(
            user_id=roster["owner_id"],
            co_owners=roster.get("co_owners", None),
            league_id=roster.get("league_id"),
            points_for=format_fantasy_points(
                roster.get("settings", None).get("fpts", 0),
                roster.get("settings", None).get("fpts_decimal", 0),
            ),
            points_against=format_fantasy_points(
                roster.get("settings", None).get("fpts_against", 0),
                roster.get("settings", None).get("fpts_against_decimal", 0),
            ),
            wins=roster.get("settings", None).get("wins", 0),
            losses=roster.get("settings", None).get("losses", 0),
            ties=roster.get("settings").get("ties", 0),
            roster_id=roster.get("roster_id"),
            players=get_player_info(roster.get("players", None)),
            starters=get_player_info(roster.get("starters", None)),
            record=roster.get("metadata", None).get("record", None),
            streak=roster.get("metadata", None).get("streak", None),
        )

    for user in users:
        username = ""
        if user.get("metadata", "display_name").get("team_name") == None:
            username = user.get("display_name")
        else:
            username = user.get("metadata", "display_name").get("team_name")

        member[user["user_id"]]["user"] = User(
            user_id=user["user_id"],
            display_name=user["display_name"],
            league_id=user["league_id"],
            team_name=username,
        )
    return member
