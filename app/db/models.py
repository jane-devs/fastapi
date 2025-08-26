# app/db/models.py
from __future__ import annotations

from datetime import date, datetime
from sqlalchemy import Date, Text, TIMESTAMP, MetaData
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.schema import Index

# naming convention — чтобы Alembic генерил стабильные имена
convention = {
    "ix": "ix_%(column_0_label)s",
    "uq": "uq_%(table_name)s_%(column_0_name)s",
    "ck": "ck_%(table_name)s_%(constraint_name)s",
    "fk": "fk_%(table_name)s_%(column_0_name)s_%(referred_table_name)s",
    "pk": "pk_%(table_name)s",
}

class Base(DeclarativeBase):
    """Базовый Declarative класс c naming convention."""
    metadata = MetaData(naming_convention=convention)


class SpimexTradingResult(Base):
    """
    Строка из таблицы spimex_trading_results.

    В БД сейчас много колонок типа TEXT (в т.ч. числовые volume/total/count).
    Приведём их к числам отдельной миграцией позже.
    """
    __tablename__ = "spimex_trading_results"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)

    exchange_product_id: Mapped[str] = mapped_column(Text)
    exchange_product_name: Mapped[str] = mapped_column(Text)

    oil_id: Mapped[str] = mapped_column(Text, index=True)

    delivery_basis_id: Mapped[str] = mapped_column(Text, index=True)
    delivery_basis_name: Mapped[str] = mapped_column(Text)

    delivery_type_id: Mapped[str] = mapped_column(Text, index=True)

    volume: Mapped[str] = mapped_column(Text)
    total:  Mapped[str] = mapped_column(Text)
    count:  Mapped[str] = mapped_column(Text)

    date: Mapped[date] = mapped_column(Date, index=True)

    created_on: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=False), nullable=True)
    updated_on: Mapped[datetime | None] = mapped_column(TIMESTAMP(timezone=False), nullable=True)

    __table_args__ = (
        Index("ix_str_composite", "oil_id", "delivery_type_id", "delivery_basis_id", "date"),
    )
