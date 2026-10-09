from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.scheduler import trigger_sector_scraping

app = FastAPI(title="Rwanda Sector Data Aggregator API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class SectorSyncRequest(BaseModel):
    target_url: str

@app.get("/health")
async def health_check():
    return {"status": "ok"}

@app.post("/v1/sectors/{sector_name}/sync")
async def sync_sector_data(sector_name: str, request_data: SectorSyncRequest):
    task = trigger_sector_scraping.delay(sector_name, request_data.target_url)
    return JSONResponse(
        status_code=202,
        content={
            "status": "queued",
            "task_id": task.id,
            "message": f"Data aggregation worker spun up for sector: {sector_name}"
        }
    )
