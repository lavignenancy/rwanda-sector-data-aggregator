import uvicorn
import asyncio
from app.database import engine, Base
from app.main import app

async def init_models():
    async with engine.begin() as conn:
        # Code block creates missing PostgreSQL relations safely on startup
        await conn.run_sync(Base.metadata.create_all)

def main():
    asyncio.run(init_models())
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )

if __name__ == "__main__":
    main()
