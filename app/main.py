from fastapi import FastAPI, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from . import models, schemas, crud
from .database import AsyncSessionLocal, engine, Base

app = FastAPI()

# Создаём таблицы при запуске
@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

# Зависимость для сессии
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

# POST /notes — создать заметку
@app.post("/notes", response_model=schemas.NoteOut)
async def create_note(note: schemas.NoteCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_note(db, note)

# GET /notes — получить список всех заметок
@app.get("/notes", response_model=List[schemas.NoteOut])
async def read_notes(db: AsyncSession = Depends(get_db)):
    return await crud.get_notes(db)
