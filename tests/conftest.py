import pytest
from datetime import date, datetime

from httpx import AsyncClient
from httpx import ASGITransport
from asgi_lifespan import LifespanManager

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.pool import StaticPool

from fakeredis.aioredis import FakeRedis

from app.db.models import Base, SpimexTradingResult
from app.db.session import get_session as prod_get_session
from app.core.config import settings
from app.main import app as fastapi_app


@pytest.fixture(scope="session")
def anyio_backend():
    """Разрешаем pytest-asyncio/anyio работать поверх asyncio-цикла для всех async-тестов."""
    return "asyncio"


@pytest.fixture(scope="session")
def fake_redis():
    """
    Фикстура фейкового Redis.

    Используем fakeredis.aioredis.FakeRedis, чтобы тестировать кеш без настоящего Redis.
    """
    return FakeRedis(decode_responses=False)


@pytest.fixture(scope="session")
def test_engine():
    """
    Отдельный async-движок SQLite (in-memory) для тестов.

    StaticPool + одинаковый URI "sqlite+aiosqlite:///:memory:" позволяют делиться
    одним соединением внутри процесса.
    """
    engine = create_async_engine(
        "sqlite+aiosqlite:///:memory:",
        poolclass=StaticPool,
        future=True,
    )
    return engine


@pytest.fixture(scope="session")
async def create_test_schema(test_engine):
    """
    Однократное создание схемы таблиц в тестовой БД.

    Вызывается в начале сессии: создаёт все таблицы и в конце всё дропает.
    """
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.fixture
async def db_session(test_engine, create_test_schema):
    """
    Транзакционная сессия к тестовой БД на каждый тест.

    Каждый тест получает чистую транзакцию, которая откатывается после выполнения,
    чтобы тесты не влияли друг на друга.
    """
    maker = async_sessionmaker(test_engine, expire_on_commit=False, class_=AsyncSession)
    async with maker() as session:
        # начинаем SAVEPOINT для изоляции теста
        trans = await session.begin()
        try:
            yield session
        finally:
            await trans.rollback()  # откатываем все изменения


@pytest.fixture(autouse=True)
def _override_dependencies(db_session, fake_redis):
    """
    Автоматическая подмена зависимостей FastAPI:
    - get_session -> наш тестовый db_session
    - get_redis   -> фейковый Redis

    Это делает все эндпойнты в тестах детерминированными и изолированными.
    """
    from app.api.routers import get_redis as prod_get_redis
    from app import api as _

    async def _test_get_session():
        yield db_session

    async def _test_get_redis():
        yield fake_redis

    fastapi_app.dependency_overrides[prod_get_session] = _test_get_session
    fastapi_app.dependency_overrides[prod_get_redis] = _test_get_redis
    try:
        yield
    finally:
        fastapi_app.dependency_overrides.clear()


@pytest.fixture(scope="session")
async def app():
    """
    Экземпляр FastAPI приложения, поднятый с учетом lifespan.

    Если у тебя фабрика приложений (create_app), используй её. Здесь — импорт из app.main.
    """
    async with LifespanManager(fastapi_app):
        yield fastapi_app


@pytest.fixture
async def client(app):
    """
    HTTP-клиент для end-to-end тестов.

    httpx>=0.28: вместо устаревшего аргумента app= используем ASGITransport.
    """
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as ac:
        yield ac


@pytest.fixture
async def seed_trading_rows(db_session):
    """
    Сидирует минимальные и валидные строки SpimexTradingResult в тестовую БД.

    Почему так:
    - Поле `date` — это именно datetime.date (SQLite/SQLAlchemy не примет строку).
    - Заполняем все NOT NULL поля из модели и обязательные поля из схемы TradingResult.
    - Не добавляем полей, которых нет в модели/схеме (например, oil_name, delivery_type_name).
    """
    rows = [
        SpimexTradingResult(
            exchange_product_id="100",
            exchange_product_name="ДТ Л-0,2-62",
            oil_id="O1",
            delivery_basis_id="BAS1",
            delivery_basis_name="Санкт-Петербург",
            delivery_type_id="DT1",
            volume="10",
            total="1000",
            count="1",
            date=date(2023, 1, 10),
            created_on=None,
            updated_on=None,
        ),
        SpimexTradingResult(
            exchange_product_id="101",
            exchange_product_name="АИ-95",
            oil_id="O2",
            delivery_basis_id="BAS2",
            delivery_basis_name="Москва",
            delivery_type_id="DT2",
            volume="20",
            total="2000",
            count="2",
            date=date(2023, 1, 11),
            created_on=None,
            updated_on=None,
        ),
    ]
    db_session.add_all(rows)
    await db_session.flush()
    return rows
