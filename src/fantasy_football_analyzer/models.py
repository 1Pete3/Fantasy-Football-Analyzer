from pydantic import BaseModel


class User(BaseModel):
    user_id: str
    display_name: str
    league_id: str
    team_name: str


class Player(BaseModel):
    first_name: str
    last_name: str
    position: str


class Roster(BaseModel):
    user_id: str | None
    co_owners: list[str] | None = None
    keepers: list[str] | None = None
    league_id: str
    record: str | None = None
    streak: str | None = None
    points_for: float
    points_against: float
    wins: int
    losses: int
    ties: int
    roster_id: int
    players: list[dict[str, Player]]
    reserve: list[dict[str, Player]] | None = None
    starters: list[dict[str, Player]] | None = None


class Member(BaseModel):
    user: User | None = None
    roster: Roster
