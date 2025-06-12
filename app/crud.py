from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
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
