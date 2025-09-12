from datetime import date
import pytest
from app.core.config import settings

API = settings.API_V1_PREFIX


@pytest.mark.anyio
async def test_dynamics_ok(client, seed_trading_rows):
    """GET /dynamics с валидным диапазоном дат -> 200 и список записей в порядке date ASC, затем exchange_product_id ASC."""
    resp = await client.get(
        f"{API}/dynamics",
        params={"start_date": "2023-01-10", "end_date": "2023-01-11"},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list) and len(data) == 2
    assert data[0]["date"] == "2023-01-10"
    assert data[1]["date"] == "2023-01-11"


@pytest.mark.anyio
async def test_dynamics_with_filters(client, seed_trading_rows):
    """Фильтр oil_id должен сузить выборку до одной записи."""
    resp = await client.get(
        f"{API}/dynamics",
        params={
            "start_date": "2023-01-10",
            "end_date": "2023-01-11",
            "oil_id": "O2",
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["exchange_product_name"] == "АИ-95"


@pytest.mark.anyio
async def test_dynamics_pagination_limit_offset(client, seed_trading_rows):
    """
    Пагинация: limit=1, offset=1 -> вторая по порядку запись (11 января).
    Проверяем, что ORDER BY date ASC, exchange_product_id ASC соблюдается.
    """
    resp = await client.get(
        f"{API}/dynamics",
        params={
            "start_date": "2023-01-10",
            "end_date": "2023-01-11",
            "limit": 1,
            "offset": 1,
        },
    )
    assert resp.status_code == 200
    data = resp.json()
    assert len(data) == 1
    assert data[0]["date"] == "2023-01-11"


@pytest.mark.anyio
async def test_dynamics_validation_start_gt_end(client):
    """start_date > end_date -> 422 (роутер оборачивает ValueError в HTTPException)."""
    resp = await client.get(
        f"{API}/dynamics",
        params={"start_date": "2023-01-11", "end_date": "2023-01-10"},
    )
    assert resp.status_code == 422


@pytest.mark.anyio
async def test_dynamics_period_too_long(client):
    """
    Период дольше, чем settings.MAX_DYNAMICS_SPAN_DAYS -> 422.
    Берём запасом (например, 400 дней).
    """
    resp = await client.get(
        f"{API}/dynamics",
        params={"start_date": "2020-01-01", "end_date": "2021-02-05"},
    )
    assert resp.status_code == 422
