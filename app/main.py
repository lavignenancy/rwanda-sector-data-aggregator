from fastapi import FastAPI, Depends, BackgroundTasks, HTTPException
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from app.database import get_db
from app.scheduler import trigger_sector_scraping

app = FastAPI(title="Rwanda Sector Data Aggregator API")

from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/v1/sectors/{sector_name}/sync")
async def sync_sector_data(sector_name: str, target_url: str):
    task = trigger_sector_scraping.delay(sector_name, target_url)
    return JSONResponse(
        status_code=202,
        content={
            "status": "queued",
            "task_id": task.id,
            "message": f"Data aggregation worker spun up for sector: {sector_name}"
        }
    )
@app.get("/")
async def root_health_check():
    return {
        "status": "healthy",
        "service": "Rwanda Sector Data Aggregator Platform",
        "documentation": "/docs"
    }
    
