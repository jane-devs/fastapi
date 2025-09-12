import orjson
import pytest

from app.core.caching import make_cache_key, cache_set_until_cutoff, cache_get, flush_all


def test_make_cache_key_is_deterministic():
    """Одинаковые параметры в другом порядке → одинаковый sha256 → одинаковый ключ."""
    p1 = {"a": 1, "b": 2}
    p2 = {"b": 2, "a": 1}
    k1 = make_cache_key("endpoint", "v1", p1)
    k2 = make_cache_key("endpoint", "v1", p2)
    assert k1 == k2
    assert k1.startswith("svc:endpoint:v1:")


@pytest.mark.anyio
async def test_cache_set_and_get(fake_redis):
    """Значение, записанное до cutoff, должно читаться таким же объектом после десериализации."""
    key = "svc:test:v1:deadbeef"
    payload = {"x": [1, 2, 3], "ok": True}
    await cache_set_until_cutoff(fake_redis, key, payload)
    val = await cache_get(fake_redis, key)
    assert val == payload


@pytest.mark.anyio
async def test_flush_all(fake_redis):
    """flush_all очищает текущую базу Redis до пустого состояния."""
    await fake_redis.set("k", orjson.dumps({"v": 1}))
    await flush_all(fake_redis)
    assert await fake_redis.get("k") is None
