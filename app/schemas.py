from datetime import datetime
from pydantic import BaseModel, ConfigDict


class RecordOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    description: str
    sector: str
    source_name: str
    source_url: str
    item_url: str
    published_at: str
    scraped_at: datetime
    updated_at: datetime


class ScrapeResult(BaseModel):
    source: str
    status: str
    records_found: int
    records_saved: int
    error: str | None = None
