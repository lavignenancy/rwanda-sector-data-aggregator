import os

from apscheduler.schedulers.asyncio import AsyncIOScheduler

from .collection_service import collect_all

scheduler = AsyncIOScheduler(timezone="UTC")


def start_scheduler():
    if scheduler.running:
        return

    interval = int(os.getenv("COLLECTION_INTERVAL_HOURS", "24"))

    if interval < 1:
        raise ValueError("Collection interval must be at least one hour")

    scheduler.add_job(
        collect_all,
        trigger="interval",
        hours=interval,
        id="scheduled_collection",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )

    scheduler.start()


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
