import pytest

from fantasy_football_analyzer.sleeper import (
    SleeperNotFoundError,
    _get,
    _validate_week,
    session,
)


@pytest.mark.parametrize("week", [-1, 0, 19, 2000])
def test_validate_week_value_error(week):
    with pytest.raises(ValueError):
        _validate_week(week)


@pytest.mark.parametrize("week", [1, 9, 18])
def test_validate_week_valid_values(week):
    _validate_week(week)


class MockResponse:
    from_cache: bool = False

    def __init__(self, data):
        self.data = data

    def json(self):
        return self.data

    def raise_for_status(self):
        pass


def test_get_json(monkeypatch):

    def mock_get(*args, **kwargs):
        return MockResponse(
            {
                "week": 12,
                "season_type": "regular",
                "season": "2026",
                "leg": 12,
                "league_season": "2026",
                "previous_season": "2025",
                "season_start_date": "2026-09-09",
                "display_week": 12,
                "league_create_season": "2026",
                "season_has_scores": True,
            }
        )

    monkeypatch.setattr(session, "get", mock_get)
    result = _get("/state/nfl")
    assert result["season"] == "2026"


def test_get_null_json(monkeypatch):
    def mock_get_null(*args, **kwargs):
        return MockResponse(None)

    monkeypatch.setattr(session, "get", mock_get_null)
    with pytest.raises(SleeperNotFoundError):
        _get("/state/nfl")
