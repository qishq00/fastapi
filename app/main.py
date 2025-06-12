from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.security import create_access_token
from datetime import timedelta
from app.security import get_current_user
from .auth import get_current_user 



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

@app.post("/notes", response_model=schemas.NoteOut)
async def create_note(
    note: schemas.NoteCreate,
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)  # 🔐 проверка токена
):
    return await crud.create_note(db, note, current_user)


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

@app.post("/login")
async def login(user: UserLogin, db: AsyncSession = Depends(get_db)):
    db_user = await crud.authenticate_user(db, user.username, user.password)
    if not db_user:
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": db_user.username}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@app.get("/notes", response_model=List[schemas.NoteOut])
async def read_notes(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return await crud.get_notes(db)