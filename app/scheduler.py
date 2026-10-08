import asyncio
from celery import Celery
from app.config import CELERY_BROKER_URL, CELERY_RESULT_BACKEND
from app.database import AsyncSessionLocal
from app.scraper import scrape_sector_metrics

celery_app = Celery(
    "rwanda_sector_tasks",
    broker=CELERY_BROKER_URL,
    backend=CELERY_RESULT_BACKEND
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Africa/Kigali",
    enable_utc=True,
    task_track_started=True,
    worker_prefetch_multiplier=1
)

@celery_app.task(name="tasks.trigger_sector_scraping", bind=True, max_retries=3)
def trigger_sector_scraping(self, sector_name: str, target_url: str):
    async def run_scraper():
        async with AsyncSessionLocal() as db_session:
            await scrape_sector_metrics(db_session, sector_name, target_url)

    try:
        loop = asyncio.get_event_loop()
    except RuntimeError:
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)

    try:
        loop.run_until_complete(run_scraper())
    except Exception as exc:
        raise self.retry(exc=exc, countdown=60)
