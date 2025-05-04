from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import sessionmaker
from sqlalchemy import text

app = FastAPI()

DATABASE_URL = "postgresql+asyncpg://phasorer:phasor123@localhost:5432/phasordb"

engine = create_async_engine(DATABASE_URL, echo=True)  # echo=True для логов SQL
AsyncSessionLocal = async_sessionmaker(bind=engine)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.get("/test_db")
async def test_db(db: AsyncSession = Depends(get_db)):
    result = await db.execute(statement=text('select 1'))
    return {"status": "ok", "data": result.scalar()}