from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import text
import asyncio
import os 
from typing import AsyncGenerator

#database_url = os.getenv("ADEMPIERE_CONNECTION_URL")
database_url = "sqlite+aiosqlite:///:memory:"
engine = create_async_engine(url=database_url)

session_factory = async_sessionmaker(engine, expire_on_commit=False)

async def get_session() -> AsyncGenerator[AsyncSession, None]:
    async with session_factory() as session:
        yield session

class Base(DeclarativeBase):
    pass 

async def main():
    async with session_factory() as session:
        res =await session.execute(text("SELECT 1;"))
        print(res.scalar_one())
        
if __name__ == "__main__":
    asyncio.run(main())