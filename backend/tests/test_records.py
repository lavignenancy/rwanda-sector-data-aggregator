import hashlib
import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.database import Base, get_db
from app.main import app

API_KEY = "test-ingestion-key"
SOURCE_URL = "https://example.org/demo"


def fingerprint(name, sector, district, province):
    values = [
        name.strip().lower(),
        sector.strip().lower(),
        district.strip().lower(),
        province.strip().lower(),
    ]
    payload = json.dumps(values, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def make_record(
    name="Kigali Business",
    sector="Trade",
    district="Gasabo",
    province="Kigali",
):
    return {
        "name": name,
        "sector": sector,
        "district": district,
        "province": province,
        "sourceUrl": SOURCE_URL,
        "fingerprint": fingerprint(name, sector, district, province),
    }


@pytest.fixture
def client(monkeypatch):
    monkeypatch.setenv("INGESTION_API_KEY", API_KEY)

    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )

    Base.metadata.create_all(bind=engine)

    testing_session = sessionmaker(bind=engine, expire_on_commit=False)

    def override_get_db():
        with testing_session() as session:
            yield session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()
        Base.metadata.drop_all(bind=engine)
        engine.dispose()


def ingest(client, records, api_key=API_KEY):
    return client.post(
        "/records/ingest",
        json={"records": records},
        headers={"X-API-Key": api_key},
    )


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_empty_records(client):
    response = client.get("/records")

    assert response.status_code == 200
    assert response.json() == []


def test_create_record(client):
    response = ingest(client, [make_record()])

    assert response.status_code == 200
    assert response.json() == {
        "received": 1,
        "created": 1,
        "updated": 0,
        "unchanged": 0,
    }

    records = client.get("/records").json()

    assert len(records) == 1
    assert records[0]["name"] == "Kigali Business"
    assert records[0]["sector"] == "Trade"


def test_duplicate_detection(client):
    record = make_record()

    first = ingest(client, [record])
    second = ingest(client, [record])

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["created"] == 0
    assert second.json()["unchanged"] == 1
    assert len(client.get("/records").json()) == 1


def test_record_update(client):
    original = make_record()
    updated = make_record(sector="Agriculture")

    first = ingest(client, [original])
    second = ingest(client, [updated])

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json()["updated"] == 1

    records = client.get("/records").json()

    assert len(records) == 1
    assert records[0]["sector"] == "Agriculture"


def test_change_history(client):
    original = make_record()
    updated = make_record(sector="Technology")

    ingest(client, [original])
    ingest(client, [updated])

    record_id = client.get("/records").json()[0]["id"]

    response = client.get(f"/records/{record_id}/changes")

    assert response.status_code == 200

    changes = response.json()

    assert len(changes) == 1
    assert changes[0]["previous_fingerprint"] == original["fingerprint"]
    assert changes[0]["new_fingerprint"] == updated["fingerprint"]


def test_reject_invalid_api_key(client):
    response = ingest(
        client,
        [make_record()],
        api_key="wrong-key",
    )

    assert response.status_code == 401
    assert client.get("/records").json() == []


def test_reject_missing_api_key(client):
    response = client.post(
        "/records/ingest",
        json={"records": [make_record()]},
    )

    assert response.status_code == 401


def test_reject_invalid_fingerprint(client):
    record = make_record()
    record["fingerprint"] = "0" * 64

    response = ingest(client, [record])

    assert response.status_code == 422
    assert client.get("/records").json() == []


def test_get_record_by_id(client):
    ingest(client, [make_record()])

    record_id = client.get("/records").json()[0]["id"]

    response = client.get(f"/records/{record_id}")

    assert response.status_code == 200
    assert response.json()["id"] == record_id


def test_missing_record_returns_404(client):
    response = client.get("/records/99999")

    assert response.status_code == 404


def test_multiple_records(client):
    records = [
        make_record(name="Business A"),
        make_record(name="Business B"),
        make_record(name="Business C"),
    ]

    response = ingest(client, records)

    assert response.status_code == 200
    assert response.json()["created"] == 3
    assert len(client.get("/records").json()) == 3


def test_ingestion_rollback_on_invalid_record(client):
    valid = make_record(name="Valid Business")
    invalid = make_record(name="Invalid Business")
    invalid["fingerprint"] = "0" * 64

    response = ingest(client, [valid, invalid])

    assert response.status_code == 422
    assert client.get("/records").json() == []
