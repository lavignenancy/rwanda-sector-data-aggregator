from contextlib import asynccontextmanager

from fastapi import FastAPI

from . import models
from .api.records import router as records_router
from .database import Base, engine


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="Rwanda Sector Data Aggregator",
    version="1.0.0",
    lifespan=lifespan,
)

app.include_router(records_router)


@app.get("/health")
def health():
    return {"status": "healthy"}