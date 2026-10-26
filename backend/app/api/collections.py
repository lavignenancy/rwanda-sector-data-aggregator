import os
import secrets
from datetime import datetime

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from pydantic import BaseModel, ConfigDict

from ..services.collection_service import collect_all, list_runs
from ..services.collection_sources import get_sources

router = APIRouter(prefix="/collections", tags=["Collections"])


class CollectionRunResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    source_name: str
    source_url: str
    status: str
    extracted: int
    created: int
    updated: int
    unchanged: int
    error_message: str | None
    started_at: datetime
    finished_at: datetime | None


def verify_api_key(x_api_key: str | None = Header(default=None)):
    expected = os.getenv("INGESTION_API_KEY")

    if not expected or not x_api_key or not secrets.compare_digest(expected, x_api_key):
        raise HTTPException(status_code=401, detail="Invalid API key")


@router.get("/sources", dependencies=[Depends(verify_api_key)])
def get_collection_sources():
    return [{"name": source.name, "url": source.url} for source in get_sources()]


@router.get(
    "/runs",
    response_model=list[CollectionRunResponse],
    dependencies=[Depends(verify_api_key)],
)
def get_collection_runs(limit: int = Query(100, ge=1, le=500)):
    return list_runs(limit)


@router.post(
    "/run",
    response_model=list[CollectionRunResponse],
    dependencies=[Depends(verify_api_key)],
)
async def trigger_collection():
    return await collect_all()
