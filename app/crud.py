from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from . import models, schemas
from .security import get_password_hash, verify_password


# Создание заметки
async def create_note(db: AsyncSession, note: schemas.NoteCreate, user_id: int):
    new_note = models.Note(**note.dict(), owner_id=user_id)
    db.add(new_note)
    await db.commit()
    await db.refresh(new_note)
    return new_note

async def get_notes(db: AsyncSession, user_id: int):
    result = await db.execute(select(models.Note).where(models.Note.owner_id == user_id))
    return result.scalars().all()

async def get_note(db: AsyncSession, note_id: int, user_id: int):
    result = await db.execute(select(models.Note).where(models.Note.id == note_id, models.Note.owner_id == user_id))
    note = result.scalars().first()
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note

async def update_note(db: AsyncSession, note_id: int, note_update: schemas.NoteUpdate, user_id: int):
    note = await get_note(db, note_id, user_id)
    for field, value in note_update.dict().items():
        setattr(note, field, value)
    await db.commit()
    await db.refresh(note)
    return note

async def delete_note(db: AsyncSession, note_id: int, user_id: int):
    note = await get_note(db, note_id, user_id)
    await db.delete(note)
    await db.commit()
    return {"detail": "Note deleted"}