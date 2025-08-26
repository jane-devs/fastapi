"""DB session and engine initialization for the microservice."""

from contextlib import asynccontextmanager
from fastapi import FastAPI
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from redis.asyncio import Redis

from app.core.config import settings
from app.core.caching import flush_all
from app.api.routers import router as spimex_router

scheduler: AsyncIOScheduler | None = None
redis_client: Redis | None = None


tags_metadata = [
    {
        "name": "spimex",
        "description": "Эндпойнты для чтения агрегированных результатов торгов СПбМТСБ.",
        "externalDocs": {
            "description": "Описание проекта",
        },
    }
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Инициализируем Redis и планировщик.
    Ежедневно в 14:11 (settings.CACHE_TZ) выполняем flush_all().
    """
    global scheduler, redis_client
    redis_client = Redis.from_url(settings.REDIS_URL, encoding="utf-8", decode_responses=False)

    scheduler = AsyncIOScheduler(timezone=settings.CACHE_TZ)
    scheduler.add_job(
        flush_all,
        trigger=CronTrigger(hour=settings.CACHE_RESET_HOUR, minute=settings.CACHE_RESET_MINUTE),
        args=[redis_client],
        id="daily-cache-flush",
        replace_existing=True,
    )
    scheduler.start()
    try:
        yield
    finally:
        if scheduler:
            scheduler.shutdown(wait=False)
        if redis_client:
            await redis_client.aclose()

app = FastAPI(
    title="Spimex Trading Microservice",
    description=(
        "Микросервис для доступа к данным таблицы `spimex_trading_results`.\n\n"
        "Предоставляет 3 эндпойнта:\n"
        "1) **/trading-dates** — последние торговые даты;\n"
        "2) **/dynamics** — динамика за период с фильтрами;\n"
        "3) **/trading-results** — результаты последнего торгового дня.\n\n"
        "Кеширование всех ответов — до ближайшего 14:11 по `settings.CACHE_TZ`."
    ),
    version="1.0.0",
    contact={"name": "Team", "email": "team@example.com"},
    license_info={"name": "MIT"},
    terms_of_service="https://example.com/tos",
    openapi_tags=tags_metadata,
    lifespan=lifespan,
)
app.include_router(spimex_router)
