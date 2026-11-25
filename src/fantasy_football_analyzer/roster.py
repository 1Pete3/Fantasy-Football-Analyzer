import os

from dotenv import load_dotenv
from rich import print

from fantasy_football_analyzer.sleeper import get_rosters, get_users_in_league

load_dotenv()

users = get_users_in_league(os.getenv("SLEEPER_LEAGUE_ID"))
rosters = get_rosters(os.getenv("SLEEPER_LEAGUE_ID"))

print(rosters)
