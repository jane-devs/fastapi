import pytest
from fakeredis.aioredis import FakeRedis

from app.services.spimex_service import SpimexService
from app.core.config import settings
from app.schemas.spimex import TradingResult


class DummyRepo:
    """Простейший мок репозитория: отдаёт фиксированные данные."""
    async def get_trading_results_for_last_day(self, oil_id=None, delivery_type_id=None, delivery_basis_id=None):
        return []


@pytest.mark.anyio
async def test_get_trading_results_cache_hit(monkeypatch):
    """
    Если в Redis уже лежит кэш, сервис обязан вернуть данные из него без вызова репозитория.
    """
    session = object()
    redis = FakeRedis(decode_responses=False)

    cached = [{
        "id": 1,
        "exchange_product_id": "100",
        "exchange_product_name": "TEST",
        "oil_id": "O1",
        "delivery_basis_id": "B1",
        "delivery_basis_name": "Санкт-Петербург",
        "delivery_type_id": "D1",
        "volume": "1",
        "total": "10",
        "count": "1",
        "date": "2023-01-10",
        "created_on": None,
        "updated_on": None,
    }]

    svc = SpimexService(session, redis)
    dummy_repo = DummyRepo()
    monkeypatch.setattr(svc, "repo", dummy_repo)
    from app.core.caching import make_cache_key, cache_set_until_cutoff
    key = make_cache_key("trading_results_last_day", "v1", {"oil_id": None, "delivery_type_id": None, "delivery_basis_id": None})
    await cache_set_until_cutoff(redis, key, cached)

    res = await svc.get_trading_results(oil_id=None, delivery_type_id=None, delivery_basis_id=None)
    assert isinstance(res, list) and isinstance(res[0], TradingResult)
    assert res[0].exchange_product_name == "TEST"


def test_get_last_trading_dates_validates_days():
    """
    days должен быть в [1..MAX_LAST_DATES]; меньше 1 или больше MAX — ValueError.
    """
    svc = SpimexService(session=object(), redis=object())
    with pytest.raises(ValueError):
        import asyncio
        asyncio.run(svc.get_last_trading_dates(0))
