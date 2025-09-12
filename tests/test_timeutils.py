from datetime import datetime, timezone
from app.core.timeutils import seconds_until_next_cutoff


def test_seconds_until_next_cutoff_before_cutoff():
    """До 14:11 — TTL это разница в пределах одного дня."""
    now_utc = datetime(2023, 1, 10, 10, 0, 0, tzinfo=timezone.utc)
    ttl = seconds_until_next_cutoff(now_utc, "Europe/Moscow", 14, 11)
    assert 0 < ttl < 6 * 3600


def test_seconds_until_next_cutoff_after_cutoff():
    """После 14:11 — TTL должен быть до завтрашнего 14:11."""
    now_utc = datetime(2023, 1, 10, 14, 30, 0, tzinfo=timezone.utc)
    ttl = seconds_until_next_cutoff(now_utc, "Europe/Moscow", 14, 11)
    assert 6 * 3600 < ttl <= 24 * 3600
