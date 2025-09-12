"""DB session and engine initialization for the microservice."""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.repositories.spimex_repo import SpimexRepository
from app.schemas.spimex import TradingResult, TradingDatesResponse, DynamicsQuery
from app.core.config import settings
from app.core.caching import make_cache_key, cache_get, cache_set_until_cutoff


class SpimexService:
    """
    Сервисный слой: валидация + кеширование + репозиторий.
    """

    def __init__(self, session: AsyncSession, redis: Redis) -> None:
        """
        :param session: AsyncSession для БД.
        :param redis: Redis-клиент для кеширования.
        """
        self.repo = SpimexRepository(session)
        self.redis = redis

    async def get_last_trading_dates(self, days: int) -> TradingDatesResponse:
        """
        Последние N торговых дат (N обязателен — смысл функции).
        Кешируется до ближайшего 14:11 (настройки в settings).
        """
        if days <= 0 or days > settings.MAX_LAST_DATES:
            raise ValueError(f"days must be in [1..{settings.MAX_LAST_DATES}]")
        key = make_cache_key("last_trading_dates", "v1", {"days": days})
        cached = await cache_get(self.redis, key)
        if cached is not None:
            return TradingDatesResponse.model_validate(cached)

        dates = await self.repo.get_last_trading_dates(days)
        payload = TradingDatesResponse(dates=dates).model_dump()
        await cache_set_until_cutoff(self.redis, key, payload)
        return TradingDatesResponse.model_validate(payload)

    async def get_dynamics(self, q: DynamicsQuery) -> List[TradingResult]:
        """
        Динамика торгов: обязательны start_date, end_date; остальные фильтры опциональны.
        Период ограничиваем настройкой, чтобы не убить БД.
        Кеш до 14:11.
        """
        if q.start_date > q.end_date:
            raise ValueError("start_date must be <= end_date")
        if (q.end_date - q.start_date).days > settings.MAX_DYNAMICS_SPAN_DAYS:
            raise ValueError(f"period too long (> {settings.MAX_DYNAMICS_SPAN_DAYS} days)")

        key = make_cache_key("dynamics", "v1", q.model_dump())
        cached = await cache_get(self.redis, key)
        if cached is not None:
            return [TradingResult(**item) for item in cached]

        rows = await self.repo.get_dynamics(
            q.start_date, q.end_date, q.oil_id, q.delivery_type_id, q.delivery_basis_id, q.limit, q.offset
        )
        data = [TradingResult.model_validate(r).model_dump() for r in rows]
        await cache_set_until_cutoff(self.redis, key, data)
        return [TradingResult(**item) for item in data]

    async def get_trading_results(
        self,
        oil_id: Optional[str],
        delivery_type_id: Optional[str],
        delivery_basis_id: Optional[str],
    ) -> List[TradingResult]:
        """
        Последние торги: записи за последний торговый день.
        Фильтры опциональны. Кеш до 14:11.
        """
        params: Dict[str, Any] = {
            "oil_id": oil_id,
            "delivery_type_id": delivery_type_id,
            "delivery_basis_id": delivery_basis_id,
        }
        key = make_cache_key("trading_results_last_day", "v1", params)
        cached = await cache_get(self.redis, key)
        if cached is not None:
            return [TradingResult(**item) for item in cached]

        rows = await self.repo.get_trading_results_for_last_day(oil_id, delivery_type_id, delivery_basis_id)
        data = [TradingResult.model_validate(r).model_dump() for r in rows]
        await cache_set_until_cutoff(self.redis, key, data)
        return [TradingResult(**item) for item in data]
