from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from .database import async_session

async def get_db() -> AsyncSession:
    async with async_session() as session:
        yield session
