from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List

from .schemas import UserCreate, UserLogin, UserOut, NoteCreate, NoteRead
from . import models, schemas, crud
from .database import AsyncSessionLocal, engine, Base

app = FastAPI()

@app.on_event("startup")
async def on_startup():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session

@app.post("/notes", response_model=NoteRead)
async def create_note(note: NoteCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_note(db, note)

@app.get("/notes", response_model=List[NoteRead])
async def read_notes(db: AsyncSession = Depends(get_db)):
    return await crud.get_notes(db)

@app.post("/register", response_model=UserOut)
async def register_user(user: UserCreate, db: AsyncSession = Depends(get_db)):
    return await crud.create_user(db, user)

@app.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    db_user = await crud.authenticate_user(db, user.username, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    return {"message": "Login successful"}
