import pytest

from app.core.config import settings

API = settings.API_V1_PREFIX


@pytest.mark.anyio
async def test_trading_results_ok(client, seed_trading_rows):
    """GET /trading-results без фильтров → 200 и непустой список для последнего дня."""
    resp = await client.get(f"{API}/trading-results")
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 1
    assert {"exchange_product_id", "exchange_product_name", "date"}.issubset(data[0].keys())


@pytest.mark.anyio
async def test_trading_results_with_filters(client, seed_trading_rows):
    """GET /trading-results с oil_id фильтрует строки."""
    resp = await client.get(f"{API}/trading-results", params={"oil_id": "O2"})
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["exchange_product_name"] == "АИ-95"


@pytest.mark.anyio
async def test_trading_dates_validation_error(client):
    """
    GET /trading-dates?days=0 → ожидаем 422 (валидация на уровне эндпойнта/сервиса)
    или 400/422 — зависит от твоей реализации. Проверяем, что НЕ 200.
    """
    resp = await client.get(f"{API}/trading-dates", params={"days": 0})
    assert resp.status_code in (400, 422)
