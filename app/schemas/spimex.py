from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict

class TradingResult(BaseModel):
    """
    Публичная схема записи торгов.

    ⚠ Обрати внимание: volume/total/count пока TEXT в БД, поэтому типы здесь str.
    После миграции к числам поменяешь их на int.
    """
    model_config = ConfigDict(from_attributes=True)

    id: int
    exchange_product_id: str
    exchange_product_name: str

    oil_id: str
    delivery_basis_id: str
    delivery_basis_name: str
    delivery_type_id: str

    volume: str
    total: str
    count: str

    date: date
    created_on: date | None = None
    updated_on: date | None = None

class TradingDatesResponse(BaseModel):
    """Ответ со списком последних торговых дат (DESC)."""
    dates: List[date] = Field(..., description="Последние N торговых дат по убыванию")

class DynamicsQuery(BaseModel):
    """
    Внутренняя схема валидированных фильтров для динамики.
    """
    start_date: date
    end_date: date
    oil_id: Optional[str] = None
    delivery_type_id: Optional[str] = None
    delivery_basis_id: Optional[str] = None
    limit: Optional[int] = None
    offset: Optional[int] = None
