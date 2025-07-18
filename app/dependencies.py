from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from .database import async_session
from typing import AsyncGenerator

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session() as session:
        yield session

