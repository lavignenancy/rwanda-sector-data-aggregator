from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, HttpUrl


class RecordInput(BaseModel):
    name: str = Field(min_length=1, max_length=255)
    sector: str = Field(min_length=1, max_length=255)
    district: str = Field(min_length=1, max_length=255)
    province: str = Field(min_length=1, max_length=255)
    sourceUrl: HttpUrl
    fingerprint: str = Field(pattern=r"^[a-f0-9]{64}$")


class IngestionRequest(BaseModel):
    records: list[RecordInput]


class IngestionResult(BaseModel):
    received: int
    created: int
    updated: int
    unchanged: int


class RecordResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    sector: str
    district: str
    province: str
    source_url: str
    fingerprint: str
    created_at: datetime
    updated_at: datetime


class ChangeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    record_id: int
    previous_fingerprint: str
    new_fingerprint: str
    changed_at: datetime