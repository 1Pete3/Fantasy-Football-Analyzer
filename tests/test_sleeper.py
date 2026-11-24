import pytest

from fantasy_football_analyzer.sleeper import _validate_week


@pytest.mark.parametrize("week", [-1, 0, 19, 2000])
def test_validate_week_value_error(week):
    with pytest.raises(ValueError):
        _validate_week(week)


@pytest.mark.parametrize("week", [1, 9, 18])
def test_validate_week_valid_values(week):
    _validate_week(week)
