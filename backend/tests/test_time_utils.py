from datetime import datetime

from app.utils.time_utils import from_unix_seconds, parse_date


def test_from_unix_seconds_converts_float_timestamp() -> None:
    result = from_unix_seconds(1743389554.0)
    assert isinstance(result, datetime)
    assert result.year == 2025


def test_parse_date_returns_none_for_empty_value() -> None:
    assert parse_date(None) is None
    assert parse_date("") is None
