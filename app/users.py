from fastapi import APIRouter, Depends
from auth import get_current_user
from sqlalchemy.ext.asyncio import AsyncSession
from .dependencies import get_db
from .auth import require_role
from . import models, schemas
from sqlalchemy.future import select


router = APIRouter()

@router.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}

@router.get("/admin/users", response_model=list[schemas.UserOut])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: models.User = Depends(require_role("admin"))
):
    result = await db.execute(select(models.User))
    return result.scalars().all()

