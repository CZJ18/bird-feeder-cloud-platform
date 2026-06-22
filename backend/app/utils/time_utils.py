from __future__ import annotations

from datetime import date, datetime, time, timedelta


def from_unix_seconds(value: float | int | str | None) -> datetime:
    """Convert a Unix seconds value into a naive local datetime."""
    if value is None:
        return datetime.now()
    return datetime.fromtimestamp(float(value))


def parse_date(value: str | None) -> date | None:
    if not value:
        return None
    return datetime.strptime(value, "%Y-%m-%d").date()


def day_bounds(target: date | None = None) -> tuple[datetime, datetime]:
    current = target or date.today()
    start = datetime.combine(current, time.min)
    end = datetime.combine(current, time.max)
    return start, end


def recent_threshold(seconds: int) -> datetime:
    return datetime.now() - timedelta(seconds=seconds)


def iso(dt: datetime | None) -> str | None:
    return dt.isoformat(timespec="seconds") if dt else None
