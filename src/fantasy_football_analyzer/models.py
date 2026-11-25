from pydantic import BaseModel


class User(BaseModel):
    user_id: str
    display_name: str
    league_id: str
    team_name: str


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
    players: list[str]
    reserve: list[str] | None = None
    starters: list[str]


class Member(BaseModel):
    user: User | None = None
    roster: Roster
