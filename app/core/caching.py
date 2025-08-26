import hashlib
from datetime import datetime, timezone
from typing import Any, Optional, Dict
import orjson
from redis.asyncio import Redis

from app.core.timeutils import seconds_until_next_cutoff
from app.core.config import settings


def make_cache_key(endpoint: str, version: str, params: Dict[str, Any]) -> str:
    """
    Ключ кеша: svc:{endpoint}:{version}:{sha256(sorted_params_json)}.
    """
    payload = orjson.dumps(params, option=orjson.OPT_SORT_KEYS)
    return f"svc:{endpoint}:{version}:{hashlib.sha256(payload).hexdigest()}"


async def cache_get(redis: Redis, key: str) -> Optional[Any]:
    """
    Получить значение из Redis и распарсить JSON (orjson).
    """
    raw = await redis.get(key)
    return None if raw is None else orjson.loads(raw)


async def cache_set_until_cutoff(redis: Redis, key: str, value: Any) -> None:
    """
    Сохранить JSON до ближайшего 14:11 в settings.CACHE_TZ.
    """
    ttl = seconds_until_next_cutoff(
        now=datetime.now(timezone.utc),
        tz_name=settings.CACHE_TZ,
        hour=settings.CACHE_RESET_HOUR,
        minute=settings.CACHE_RESET_MINUTE,
    )
    await redis.set(key, orjson.dumps(value), ex=ttl)


async def flush_all(redis: Redis) -> None:
    """
    Полный сброс БД Redis (текущей).
    """
    await redis.flushdb()
