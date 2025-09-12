import pytest
from datetime import date

from app.repositories.spimex_repo import SpimexRepository
from app.db.models import SpimexTradingResult


@pytest.mark.anyio
async def test_get_last_dates_desc(db_session, seed_trading_rows):
    """get_last_trading_dates(N) возвращает N уникальных дат по убыванию."""
    repo = SpimexRepository(db_session)
    dates = await repo.get_last_trading_dates(2)
    assert dates == [date(2023, 1, 11), date(2023, 1, 10)]


@pytest.mark.anyio
async def test_get_last_trading_day(db_session, seed_trading_rows):
    """MAX(date) возвращается как последний торговый день."""
    repo = SpimexRepository(db_session)
    last = await repo.get_last_trading_day()
    assert last == date(2023, 1, 11)


@pytest.mark.anyio
async def test_get_trading_results_for_last_day_with_filters(db_session, seed_trading_rows):
    """
    Проверяем, что выборка за последний торговый день корректно фильтруется по oil_id.
    У репозитория сигнатура без дефолтов, поэтому явно прокидываем None для остальных фильтров.
    """
    repo = SpimexRepository(db_session)
    rows = await repo.get_trading_results_for_last_day(
        oil_id="O2",
        delivery_type_id=None,
        delivery_basis_id=None,
    )
    assert len(rows) == 1
    assert rows[0].exchange_product_name == "АИ-95"
