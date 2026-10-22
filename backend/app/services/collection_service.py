
import asyncio
import json
import os
from datetime import UTC, datetime
from pathlib import Path

from sqlalchemy import select

from ..database import SessionLocal
from ..models import CollectionRun
from .collection_sources import CollectionSource, get_sources

PROJECT_ROOT = Path(__file__).resolve().parents[3]
PIPELINE_DIR = PROJECT_ROOT / "pipeline"


def utc_now():
    return datetime.now(UTC)


async def collect_source(source: CollectionSource) -> CollectionRun:
    with SessionLocal() as db:
        run = CollectionRun(
            source_name=source.name,
            source_url=source.url,
            status="running",
        )
        db.add(run)
        db.commit()
        db.refresh(run)
        run_id = run.id

    try:
        api_key = os.getenv("INGESTION_API_KEY")

        if not api_key:
            raise RuntimeError("INGESTION_API_KEY is not configured")

        environment = os.environ.copy()
        environment["API_URL"] = os.getenv(
            "API_URL",
            "http://127.0.0.1:8000",
        )

        command = [
            "npm",
            "run",
            "run",
            "--",
            source.url,
            "--ingest",
        ]

        if source.renderer == "playwright":
            command.append("--playwright")
        elif source.renderer != "cheerio":
            raise ValueError(
                f"Unsupported renderer: {source.renderer}"
            )

        process = await asyncio.create_subprocess_exec(
            *command,
            cwd=str(PIPELINE_DIR),
            env=environment,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
        )

        try:
            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=120,
            )
        except TimeoutError:
            process.kill()
            await process.communicate()
            raise RuntimeError(
                "Collection timed out after 120 seconds"
            )

        if process.returncode != 0:
            error_message = stderr.decode(
                "utf-8",
                errors="replace",
            ).strip()

            raise RuntimeError(
                error_message[-2000:]
                or f"Pipeline exited with code {process.returncode}"
            )

        output = json.loads(stdout.decode("utf-8"))

        ingestion = output["ingestion"]

        with SessionLocal() as db:
            run = db.get(CollectionRun, run_id)

            if run is None:
                raise RuntimeError("Collection run not found")

            run.status = "success"
            run.extracted = int(output["extracted"])
            run.created = int(ingestion["created"])
            run.updated = int(ingestion["updated"])
            run.unchanged = int(ingestion["unchanged"])
            run.finished_at = utc_now()
            run.error_message = None

            db.commit()
            db.refresh(run)
            db.expunge(run)

            return run

    except Exception as exc:
        with SessionLocal() as db:
            run = db.get(CollectionRun, run_id)

            if run is None:
                raise RuntimeError(
                    "Collection run not found"
                ) from exc

            run.status = "failed"
            run.error_message = str(exc)[:2000]
            run.finished_at = utc_now()

            db.commit()
            db.refresh(run)
            db.expunge(run)

            return run


async def collect_all() -> list[CollectionRun]:
    results = []

    for source in get_sources():
        result = await collect_source(source)
        results.append(result)

    return results


def list_runs(limit: int = 100) -> list[CollectionRun]:
    with SessionLocal() as db:
        runs = db.scalars(
            select(CollectionRun)
            .order_by(CollectionRun.id.desc())
            .limit(limit)
        ).all()

        for run in runs:
            db.expunge(run)

        return runs
