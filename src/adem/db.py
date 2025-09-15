from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase, sessionmaker
from sqlalchemy import text
import asyncio
import os 
from dotenv import load_dotenv
from typing import AsyncGenerator

load_dotenv()
database_url = os.getenv("ADEMPIERE_CONNECTION_URL")
#database_url = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(url=database_url)

session_factory = async_sessionmaker(engine, expire_on_commit=False)
AsyncSessionLocal = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session

async def get_session_for_celery():
    async with AsyncSessionLocal() as session:
        yield session

class Base(DeclarativeBase):
    pass 

async def main():
    async with session_factory() as session:
        res =await session.execute(text("SELECT 1;"))
        print(res.scalar_one())
        
if __name__ == "__main__":
    asyncio.run(main())