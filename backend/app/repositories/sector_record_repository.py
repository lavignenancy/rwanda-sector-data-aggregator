from sqlalchemy import select
from sqlalchemy.orm import Session

from ..models import RecordChange, SectorRecord


def find_by_identity(db: Session, identity_key: str):
    return db.scalar(
        select(SectorRecord).where(SectorRecord.identity_key == identity_key)
    )


def find_by_id(db: Session, record_id: int):
    return db.get(SectorRecord, record_id)


def list_records(db: Session, limit: int, offset: int):
    return db.scalars(
        select(SectorRecord)
        .order_by(SectorRecord.id)
        .offset(offset)
        .limit(limit)
    ).all()


def create_record(db: Session, **values):
    record = SectorRecord(**values)
    db.add(record)
    db.flush()
    return record


def add_change(db: Session, record_id: int, previous: str, current: str):
    change = RecordChange(
        record_id=record_id,
        previous_fingerprint=previous,
        new_fingerprint=current,
    )
    db.add(change)
    return change


def list_changes(db: Session, record_id: int):
    return db.scalars(
        select(RecordChange)
        .where(RecordChange.record_id == record_id)
        .order_by(RecordChange.id.desc())
    ).all()