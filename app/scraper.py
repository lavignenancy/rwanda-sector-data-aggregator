import hashlib
import inspect
import json
import httpx
from bs4 import BeautifulSoup
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import AggregatedSectorData

def generate_payload_signature(payload: dict) -> str:
    serialized = json.dumps(payload, sort_keys=True)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()

async def scrape_sector_metrics(db: AsyncSession, sector_name: str, target_url: str) -> None:
    async with httpx.AsyncClient(timeout=15.0) as client:
        try:
            response = await client.get(target_url)
            response.raise_for_status()
        except httpx.HTTPError:
            return

    soup = BeautifulSoup(response.text, "html.parser")
    extracted_metrics = {}
    
    for row in soup.find_all("div", class_="metric-row"):
        label_element = row.find("span", class_="metric-label")
        value_element = row.find("span", class_="metric-value")
        if label_element and value_element:
            key = label_element.text.strip().lower().replace(" ", "_")
            val = value_element.text.strip()
            extracted_metrics[key] = val

    if not extracted_metrics:
        extracted_metrics = {
            "scraped_title": soup.title.string.strip() if soup.title else "Unknown",
            "content_length": len(response.text)
        }

    signature = generate_payload_signature(extracted_metrics)

    query = select(AggregatedSectorData).where(
        AggregatedSectorData.structural_signature == signature
    )
    db_result = await db.execute(query)
    existing_record = db_result.scalars().first()

    if existing_record:
        existing_record.sector = sector_name
        await db.commit()
        return

    sector_query = select(AggregatedSectorData).where(
        AggregatedSectorData.sector == sector_name,
        AggregatedSectorData.source_url == target_url
    )
    sector_db_result = await db.execute(sector_query)
    record_to_update = sector_db_result.scalars().first()

    if record_to_update:
        record_to_update.payload = extracted_metrics
        record_to_update.structural_signature = signature
        record_to_update.data_type = "Public Sector Matrix"
    else:
        new_record = AggregatedSectorData(
            sector=sector_name,
            data_type="Public Sector Matrix",
            source_url=target_url,
            structural_signature=signature,
            payload=extracted_metrics
        )
        add_result = db.add(new_record)
        if inspect.isawaitable(add_result):
            await add_result

    await db.commit()
