"""DB session and engine initialization for the microservice."""

from datetime import date
from typing import List, Optional

from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from redis.asyncio import Redis

from app.core.config import settings
from app.db.session import get_session
from app.schemas.spimex import TradingResult, TradingDatesResponse, DynamicsQuery
from app.services.spimex_service import SpimexService

router = APIRouter(prefix=settings.API_V1_PREFIX, tags=["spimex"])


def get_redis() -> Redis:
    """
    Фабрика Redis-клиента для Depends.
    В проде лучше открывать соединение в lifespan и переиспользовать один экземпляр.
    """
    return Redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=False)


@router.get(
    "/trading-dates",
    response_model=TradingDatesResponse,
    summary="Список дат последних торговых дней",
    description=(
        "Возвращает N последних уникальных торговых дат (по убыванию). "
        "`days` обязателен по смыслу (сколько дат показать). "
        "Результат кешируется до ближайшего 14:11."
    ),
    tags=["spimex"],
    responses={
        200: {"description": "Успешный ответ со списком дат."},
        422: {"description": "Ошибка валидации параметра `days`."},
    },
)
async def get_last_trading_dates(
    days: int = Query(settings.DEFAULT_LAST_DATES, ge=1, le=settings.MAX_LAST_DATES),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    """
    Список дат последних торговых дней (DESC).
    Обязателен параметр `days` (по смыслу функции).
    """
    svc = SpimexService(session, redis)
    try:
        return await svc.get_last_trading_dates(days)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get(
    "/dynamics",
    response_model=List[TradingResult],
    summary="Динамика торгов за период",
    description=(
        "Возвращает записи за указанный период. Обязательные параметры: "
        "`start_date`, `end_date`. Фильтры `oil_id`, `delivery_type_id`, "
        "`delivery_basis_id` — опциональные. Кеш до 14:11."
    ),
    tags=["spimex"],
    responses={
        200: {"description": "Список записей торгов."},
        422: {"description": "Ошибки валидации или слишком длинный период."},
    },
)
async def get_dynamics(
    start_date: date = Query(...),
    end_date: date = Query(...),
    oil_id: Optional[str] = Query(None),
    delivery_type_id: Optional[str] = Query(None),
    delivery_basis_id: Optional[str] = Query(None),
    limit: Optional[int] = Query(None, ge=1, le=10000),
    offset: Optional[int] = Query(None, ge=0),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    """
    Динамика за период. Обязательные: start_date, end_date.
    Остальные фильтры опциональны. Пагинация — limit/offset.
    """
    svc = SpimexService(session, redis)
    try:
        return await svc.get_dynamics(DynamicsQuery(
            start_date=start_date,
            end_date=end_date,
            oil_id=oil_id,
            delivery_type_id=delivery_type_id,
            delivery_basis_id=delivery_basis_id,
            limit=limit,
            offset=offset,
        ))
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get(
    "/trading-results",
    response_model=List[TradingResult],
    summary="Результаты последнего торгового дня",
    description=(
        "Возвращает записи за **последний** торговый день. "
        "Фильтры `oil_id`, `delivery_type_id`, `delivery_basis_id` — опциональные. "
        "Кеш до 14:11."
    ),
    tags=["spimex"],
    responses={200: {"description": "Список записей последнего дня."}},
)
async def get_trading_results(
    oil_id: Optional[str] = Query(None),
    delivery_type_id: Optional[str] = Query(None),
    delivery_basis_id: Optional[str] = Query(None),
    session: AsyncSession = Depends(get_session),
    redis: Redis = Depends(get_redis),
):
    """
    Последние торги = записи за последний торговый день.
    Фильтры опциональны.
    """
    svc = SpimexService(session, redis)
    return await svc.get_trading_results(
        oil_id=oil_id,
        delivery_type_id=delivery_type_id,
        delivery_basis_id=delivery_basis_id,
    )
