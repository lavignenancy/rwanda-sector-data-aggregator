import pytest
from unittest.mock import AsyncMock, patch, MagicMock
from app.scraper import generate_payload_signature, scrape_sector_metrics

def test_generate_payload_signature():
    payload = {"population": 15000, "sector_name": "Gashora"}
    sig1 = generate_payload_signature(payload)
    sig2 = generate_payload_signature(payload)
    assert sig1 == sig2
    assert len(sig1) == 64

@pytest.mark.asyncio
@patch("httpx.AsyncClient.get")
async def test_scrape_sector_metrics_success(mock_get):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.text = '<html><div class="metric-row"><span class="metric-label">Population</span><span class="metric-value">15000</span></div></html>'
    mock_get.return_value = mock_response

    mock_scalars = MagicMock()
    mock_scalars.first.return_value = None
    
    mock_result = MagicMock()
    mock_result.scalars.return_value = mock_scalars

    mock_db = AsyncMock()
    mock_db.execute.return_value = mock_result

    await scrape_sector_metrics(mock_db, "Gashora", "https://statistics.gov.rw")
    assert mock_db.add.called
    assert mock_db.commit.called
