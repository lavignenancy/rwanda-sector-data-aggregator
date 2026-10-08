from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Index, JSON
from app.database import Base

class AggregatedSectorData(Base):
    __tablename__ = "aggregated_sector_data"

    id = Column(Integer, primary_key=True, index=True)
    sector = Column(String, nullable=False, index=True)
    data_type = Column(String, nullable=False, index=True)
    source_url = Column(String, nullable=False)
    structural_signature = Column(String, unique=True, nullable=False, index=True)
    payload = Column(JSON, nullable=False) 
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    __table_args__ = (
        Index("ix_sector_data_type", "sector", "data_type"),
    )
