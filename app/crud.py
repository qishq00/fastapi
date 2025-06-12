from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException
from . import models, schemas

async def create_note(db: AsyncSession, note: schemas.NoteCreate):
    new_note = models.Note(**note.dict())
    db.add(new_note)
    await db.commit()
    await db.refresh(new_note)
    return new_note

async def get_notes(db: AsyncSession):
    result = await db.execute(select(models.Note))
    return result.scalars().all()

async def create_user(db: AsyncSession, user: schemas.UserCreate):
    new_user = models.User(username=user.username, password=user.password)
    db.add(new_user)
    try:
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Username already exists")

async def authenticate_user(db: AsyncSession, username: str, password: str):
    result = await db.execute(select(models.User).where(models.User.username == username))
    user = result.scalars().first()
    if user and user.password == password:
        return user
    return None

