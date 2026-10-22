import os
from contextlib import asynccontextmanager

from fastapi import FastAPI

from .api.collections import router as collections_router
from .api.records import router as records_router
from .database import Base, engine
from .services.scheduler_service import start_scheduler, stop_scheduler


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)

    if os.getenv("ENABLE_COLLECTION_SCHEDULER", "false").lower() == "true":
        start_scheduler()

    try:
        yield
    finally:
        stop_scheduler()


app = FastAPI(
    title="Rwanda Sector Data Aggregator",
    version="1.1.0",
    lifespan=lifespan,
)

app.include_router(records_router)
app.include_router(collections_router)


@app.get("/health")
def health():
    return {"status": "healthy"}
