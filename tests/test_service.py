import pytest
from datetime import date

from fakeredis.aioredis import FakeRedis

from app.services.spimex_service import SpimexService
from app.core.config import settings
from app.schemas.spimex import DynamicsQuery, TradingResult
from app.core.caching import make_cache_key, cache_set_until_cutoff, cache_get


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


class _Row:
    """
    Простейшая "ORM-подобная" заглушка строки, которую Pydantic примет благодаря ConfigDict(from_attributes=True).
    Нужны только атрибуты, которые есть в TradingResult.
    """
    def __init__(self, **kw):
        for k, v in kw.items():
            setattr(self, k, v)


class _RepoMock:
    """Мок репозитория для get_dynamics: вернёт одну фиктивную запись."""
    async def get_dynamics(self, start_date, end_date, oil_id, delivery_type_id, delivery_basis_id, limit, offset):
        return [
            _Row(
                id=1,
                exchange_product_id="100",
                exchange_product_name="MOCK",
                oil_id=oil_id or "O1",
                delivery_basis_id=delivery_basis_id or "B1",
                delivery_basis_name="Санкт-Петербург",
                delivery_type_id=delivery_type_id or "D1",
                volume="1",
                total="10",
                count="1",
                date=date(2023, 1, 10),
                created_on=None,
                updated_on=None,
            )
        ]


@pytest.mark.anyio
async def test_get_dynamics_cache_hit(monkeypatch):
    """
    Если нужный ключ уже лежит в Redis — сервис должен отдать данные из кеша
    и не обращаться к репозиторию.
    """
    redis = FakeRedis(decode_responses=False)
    svc = SpimexService(session=object(), redis=redis)

    q = DynamicsQuery(start_date=date(2023, 1, 10), end_date=date(2023, 1, 11))
    key = make_cache_key("dynamics", "v1", q.model_dump())

    cached_payload = [{
        "id": 1,
        "exchange_product_id": "100",
        "exchange_product_name": "FROM_CACHE",
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
    await cache_set_until_cutoff(redis, key, cached_payload)

    # На всякий случай "отрубаем" repo, чтобы падало, если он внезапно вызовется
    monkeypatch.setattr(svc, "repo", None)

    res = await svc.get_dynamics(q)
    assert isinstance(res, list) and isinstance(res[0], TradingResult)
    assert res[0].exchange_product_name == "FROM_CACHE"


@pytest.mark.anyio
async def test_get_dynamics_repo_and_cache_write(monkeypatch):
    """
    Промах по кешу -> вызов репозитория -> сериализация -> запись в кеш -> возврат валидных TradingResult.
    """
    redis = FakeRedis(decode_responses=False)
    svc = SpimexService(session=object(), redis=redis)
    monkeypatch.setattr(svc, "repo", _RepoMock())

    q = DynamicsQuery(start_date=date(2023, 1, 10), end_date=date(2023, 1, 11), oil_id="O2")
    res = await svc.get_dynamics(q)

    # Возврат
    assert len(res) == 1
    assert res[0].exchange_product_name == "MOCK"
    assert res[0].oil_id == "O2"

    # Запись в кеш (прямо проверим наличие ключа и содержимое структуры)
    key = make_cache_key("dynamics", "v1", q.model_dump())
    cached = await cache_get(redis, key)
    assert isinstance(cached, list) and cached[0]["exchange_product_name"] == "MOCK"


def test_get_dynamics_validation_errors():
    """
    Валидация: (1) start_date > end_date; (2) период слишком длинный.
    Сервис должен кидать ValueError — это поведение роутер конвертирует в 422.
    """
    svc = SpimexService(session=object(), redis=object())

    # 1) start_date > end_date
    with pytest.raises(ValueError):
        import asyncio
        asyncio.run(svc.get_dynamics(DynamicsQuery(
            start_date=date(2023, 1, 11),
            end_date=date(2023, 1, 10),
        )))

    # 2) слишком длинный период
    long_start = date(2020, 1, 1)
    long_end = date(2021, 2, 5)  # > 366 дней
    with pytest.raises(ValueError):
        import asyncio
        asyncio.run(svc.get_dynamics(DynamicsQuery(
            start_date=long_start,
            end_date=long_end,
        )))