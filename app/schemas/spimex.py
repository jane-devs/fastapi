"""DB session and engine initialization for the microservice."""

from datetime import date
from typing import Optional, List
from pydantic import BaseModel, Field, ConfigDict


class TradingResult(BaseModel):
    """
    Публичная схема записи торгов.
    """
    model_config = ConfigDict(from_attributes=True, json_schema_extra={
        "example": {
            "id": 123,
            "exchange_product_id": "1234567",
            "exchange_product_name": "ДТ Л-0,2-62",
            "oil_id": "1001",
            "delivery_basis_id": "AB1",
            "delivery_basis_name": "Сургут",
            "delivery_type_id": "1",
            "volume": "1000",
            "total": "45000000",
            "count": "12",
            "date": "2025-01-15",
            "created_on": None,
            "updated_on": None
        }
    })

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
