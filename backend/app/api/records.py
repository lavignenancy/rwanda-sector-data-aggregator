import os
import secrets

from fastapi import APIRouter, Depends, Header, HTTPException, Query
from sqlalchemy.orm import Session

from ..database import get_db
from ..repositories import sector_record_repository as repository
from ..schemas.sector_record import (
    ChangeResponse,
    IngestionRequest,
    IngestionResult,
    RecordResponse,
)
from ..services.ingestion_service import ingest

router = APIRouter(prefix="/records", tags=["Records"])


def verify_api_key(x_api_key: str | None = Header(default=None)):
    expected = os.getenv("INGESTION_API_KEY")

    if not expected or not x_api_key or not secrets.compare_digest(
        expected, x_api_key
    ):
        raise HTTPException(status_code=401, detail="Invalid API key")


@router.post(
    "/ingest",
    response_model=IngestionResult,
    dependencies=[Depends(verify_api_key)],
)
def ingest_records(
    payload: IngestionRequest,
    db: Session = Depends(get_db),
):
    return ingest(db, payload)


@router.get("", response_model=list[RecordResponse])
def get_records(
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    return repository.list_records(db, limit, offset)


@router.get("/{record_id}", response_model=RecordResponse)
def get_record(record_id: int, db: Session = Depends(get_db)):
    record = repository.find_by_id(db, record_id)

    if record is None:
        raise HTTPException(status_code=404, detail="Record not found")

    return record


@router.get("/{record_id}/changes", response_model=list[ChangeResponse])
def get_changes(record_id: int, db: Session = Depends(get_db)):
    if repository.find_by_id(db, record_id) is None:
        raise HTTPException(status_code=404, detail="Record not found")

    return repository.list_changes(db, record_id)