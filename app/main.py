from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.security import create_access_token
from datetime import timedelta
from app.security import get_current_user
from .security import get_current_user 
from fastapi.security import OAuth2PasswordRequestForm
from auth import authenticate_user, create_access_token, ACCESS_TOKEN_EXPIRE_MINUTES
from users import router as users_router
from datetime import timedelta
from . import schemas, crud
from .dependencies import get_db
from .auth import get_current_user
from .models import User
from fastapi import APIRouter, Depends
from fastapi import Query
from app.tasks import send_email_task
from app.celery_worker import send_email_task




from .schemas import UserCreate, UserLogin, UserOut, NoteCreate, NoteRead
from . import models, schemas, crud
from .database import AsyncSessionLocal, engine, Base

app = FastAPI()
app.include_router(users_router)
router = APIRouter()




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


@app.get("/notes", response_model=list[schemas.NoteOut])
async def read_notes(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1),
    search: str = Query("", alias="search"),
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(get_current_user)
):
    return await crud.get_notes(db, user_id=current_user.id, skip=skip, limit=limit, search=search)

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

@app.post("/login")
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Неверное имя пользователя или пароль")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user["username"]},
        expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.post("/notes", response_model=schemas.NoteOut)
async def create_note(note: schemas.NoteCreate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await crud.create_note(db, note, current_user.id)

@router.get("/notes", response_model=list[schemas.NoteOut])
async def list_notes(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await crud.get_notes(db, current_user.id)

@router.get("/notes/{note_id}", response_model=schemas.NoteOut)
async def read_note(note_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await crud.get_note(db, note_id, current_user.id)

@router.put("/notes/{note_id}", response_model=schemas.NoteOut)
async def update_note(note_id: int, note: schemas.NoteUpdate, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await crud.update_note(db, note_id, note, current_user.id)

@router.delete("/notes/{note_id}")
async def delete_note(note_id: int, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    return await crud.delete_note(db, note_id, current_user.id)

@app.post("/send-email/")
def trigger_email(email: str):
    task = send_email_task.delay(email)
    return {
        "message": "Задача отправки email поставлена в очередь",
        "task_id": task.id
    }

@app.post("/trigger-task")
def trigger_task(email: str, user=Depends(get_current_user)):
    task = send_email_task.delay(email)
    return {"message": "Task started", "task_id": task.id}

@app.get("/")
def root():
    return {"message": "FastAPI + Celery + Redis работает!"}

@app.post("/send-email/")
def send_email(email: str):
    task = send_email_task.delay(email)  # Запускаем задачу в фоне
    return {"task_id": task.id, "status": "queued"}
