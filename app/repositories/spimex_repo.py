"""DB session and engine initialization for the microservice."""

from datetime import date
from typing import List, Optional, Sequence

from sqlalchemy import select, func, desc, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import SpimexTradingResult


class SpimexRepository:
    """
    Репозиторий: инкапсулирует SQL к spimex_trading_results.
    Никакой бизнес-логики — только выборки.
    """

    def __init__(self, session: AsyncSession) -> None:
        """
        :param session: Активная AsyncSession.
        """
        self.session = session

    async def get_last_trading_dates(self, days: int) -> List[date]:
        """
        Последние уникальные торговые даты (DESC) c LIMIT.
        """
        stmt = (
            select(SpimexTradingResult.date)
            .group_by(SpimexTradingResult.date)
            .order_by(desc(SpimexTradingResult.date))
            .limit(days)
        )
        return (await self.session.execute(stmt)).scalars().all()

    async def get_last_trading_day(self) -> Optional[date]:
        """
        MAX(date) — дата последнего торгового дня.
        """
        stmt = select(func.max(SpimexTradingResult.date))
        return (await self.session.execute(stmt)).scalar_one_or_none()

    async def get_dynamics(
        self,
        start_date: date,
        end_date: date,
        oil_id: Optional[str],
        delivery_type_id: Optional[str],
        delivery_basis_id: Optional[str],
        limit: Optional[int],
        offset: Optional[int],
    ) -> Sequence[SpimexTradingResult]:
        """
        Записи за период + опциональные фильтры.
        Сортировка по date ASC, затем по exchange_product_id.
        """
        conds = [
            SpimexTradingResult.date >= start_date,
            SpimexTradingResult.date <= end_date,
        ]
        if oil_id:
            conds.append(SpimexTradingResult.oil_id == oil_id)
        if delivery_type_id:
            conds.append(SpimexTradingResult.delivery_type_id == delivery_type_id)
        if delivery_basis_id:
            conds.append(SpimexTradingResult.delivery_basis_id == delivery_basis_id)

        stmt = (
            select(SpimexTradingResult)
            .where(and_(*conds))
            .order_by(
                SpimexTradingResult.date.asc(),
                SpimexTradingResult.exchange_product_id.asc(),
            )
        )
        if offset:
            stmt = stmt.offset(offset)
        if limit:
            stmt = stmt.limit(limit)

        return (await self.session.execute(stmt)).scalars().all()

    async def get_trading_results_for_last_day(
        self,
        oil_id: Optional[str],
        delivery_type_id: Optional[str],
        delivery_basis_id: Optional[str],
    ) -> Sequence[SpimexTradingResult]:
        """
        Записи за последний торговый день (MAX(date)) с опциональными фильтрами.
        """
        last = await self.get_last_trading_day()
        if not last:
            return []

        conds = [SpimexTradingResult.date == last]
        if oil_id:
            conds.append(SpimexTradingResult.oil_id == oil_id)
        if delivery_type_id:
            conds.append(SpimexTradingResult.delivery_type_id == delivery_type_id)
        if delivery_basis_id:
            conds.append(SpimexTradingResult.delivery_basis_id == delivery_basis_id)

        stmt = (
            select(SpimexTradingResult)
            .where(and_(*conds))
            .order_by(SpimexTradingResult.exchange_product_id.asc())
        )
        return (await self.session.execute(stmt)).scalars().all()
