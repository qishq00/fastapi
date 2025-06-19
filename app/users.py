from fastapi import APIRouter, Depends
from auth import get_current_user

router = APIRouter()

@router.get("/users/me")
async def read_users_me(current_user: dict = Depends(get_current_user)):
    return {"user": current_user}
