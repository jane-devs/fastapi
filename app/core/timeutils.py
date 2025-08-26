"""DB session and engine initialization for the microservice."""

from datetime import datetime, timedelta
from zoneinfo import ZoneInfo


def seconds_until_next_cutoff(now: datetime, tz_name: str, hour: int, minute: int) -> int:
    """
    Секунды до ближайшего локального cutoff (например, 14:11).
    now может быть в любой tz/UTC — функция приведёт к tz_name.
    """
    tz = ZoneInfo(tz_name)
    local_now = now.astimezone(tz)
    cutoff = local_now.replace(hour=hour, minute=minute, second=0, microsecond=0)
    if local_now >= cutoff:
        cutoff = (local_now + timedelta(days=1)).replace(hour=hour, minute=minute, second=0, microsecond=0)
    return int((cutoff - local_now).total_seconds())
