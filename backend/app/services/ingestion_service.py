import hashlib
import json
import re

from fastapi import HTTPException
from sqlalchemy.orm import Session

from ..models.sector_record import utc_now
from ..repositories import sector_record_repository as repository
from ..schemas.sector_record import IngestionRequest, IngestionResult


def normalize(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().lower()


def hash_values(values: list[str]) -> str:
    payload = json.dumps(values, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def ingest(db: Session, payload: IngestionRequest) -> IngestionResult:
    created = 0
    updated = 0
    unchanged = 0

    try:
        for item in payload.records:
            values = [
                normalize(item.name),
                normalize(item.sector),
                normalize(item.district),
                normalize(item.province),
            ]

            if hash_values(values) != item.fingerprint:
                raise HTTPException(
                    status_code=422,
                    detail="Record fingerprint does not match its content",
                )

            source_url = str(item.sourceUrl)

            identity_key = hash_values(
                [
                    source_url,
                    normalize(item.name),
                ]
            )

            existing = repository.find_by_identity(db, identity_key)

            if existing is None:
                repository.create_record(
                    db,
                    name=item.name,
                    sector=item.sector,
                    district=item.district,
                    province=item.province,
                    source_url=source_url,
                    identity_key=identity_key,
                    fingerprint=item.fingerprint,
                )
                created += 1
                continue

            if existing.fingerprint == item.fingerprint:
                unchanged += 1
                continue

            repository.add_change(
                db,
                existing.id,
                existing.fingerprint,
                item.fingerprint,
            )

            existing.name = item.name
            existing.sector = item.sector
            existing.district = item.district
            existing.province = item.province
            existing.fingerprint = item.fingerprint
            existing.updated_at = utc_now()

            updated += 1

        db.commit()

    except Exception:
        db.rollback()
        raise

    return IngestionResult(
        received=len(payload.records),
        created=created,
        updated=updated,
        unchanged=unchanged,
    )
