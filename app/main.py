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

app = FastAPI(title=settings.APP_NAME, lifespan=lifespan)
app.include_router(spimex_router)
