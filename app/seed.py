from datetime import datetime, timezone

from .database import SessionLocal, init_db
from .models import SectorRecord

DEMO = [
    {
        "title": "Demo: Community health information update",
        "description": "Example record used to demonstrate the dashboard and API.",
        "sector": "health",
        "source_name": "Demo Source",
        "source_url": "https://example.org/health",
        "item_url": "https://example.org/health/demo-1",
        "published_at": "2026-10-05",
        "content_hash": "demo-health-001",
    },
    {
        "title": "Demo: Agricultural sector information",
        "description": "Example record used to demonstrate sector filtering.",
        "sector": "agriculture",
        "source_name": "Demo Source",
        "source_url": "https://example.org/agriculture",
        "item_url": "https://example.org/agriculture/demo-1",
        "published_at": "2026-10-05",
        "content_hash": "demo-agriculture-001",
    },
    {
        "title": "Demo: Education sector update",
        "description": "Example record used to demonstrate the public dashboard.",
        "sector": "education",
        "source_name": "Demo Source",
        "source_url": "https://example.org/education",
        "item_url": "https://example.org/education/demo-1",
        "published_at": "2026-10-05",
        "content_hash": "demo-education-001",
    },
]


def main():
    init_db()
    db = SessionLocal()
    try:
        if db.query(SectorRecord).count():
            print("Database already contains records; nothing seeded.")
            return

        now = datetime.now(timezone.utc)
        for item in DEMO:
            db.add(SectorRecord(**item, scraped_at=now, updated_at=now))
        db.commit()
        print(f"Seeded {len(DEMO)} demo records.")
    finally:
        db.close()


if __name__ == "__main__":
    main()
