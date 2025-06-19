from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.exc import IntegrityError
from fastapi import HTTPException

from . import models, schemas
from .security import get_password_hash, verify_password


# Создание заметки
async def create_note(db: AsyncSession, note: schemas.NoteCreate, user: models.User):
    new_note = models.Note(**note.dict(), owner_id=user.id)
    db.add(new_note)
    await db.commit()
    await db.refresh(new_note)
    return new_note



# Получение всех заметок
async def get_notes(db: AsyncSession):
    result = await db.execute(select(models.Note))
    return result.scalars().all()


# Регистрация пользователя
async def create_user(db: AsyncSession, user: schemas.UserCreate):
    hashed_password = get_password_hash(user.password)
    new_user = models.User(username=user.username, hashed_password=hashed_password)
    db_user = models.User(
        username=user.username,
        password=hashed_password,
        role="user"
    )
    db.add(new_user)

    try:
        await db.commit()
        await db.refresh(new_user)
        return new_user
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Username already exists")


# Аутентификация пользователя
async def authenticate_user(db: AsyncSession, username: str, password: str):
    result = await db.execute(select(models.User).where(models.User.username == username))
    user = result.scalar_one_or_none()
    if user and verify_password(password, user.password):  # пароль из БД теперь хешированный
        return user
    return None

