from fastapi import APIRouter, Depends
from app.dependencies import get_current_active_user
from app.models import user_models
from app.schemas import schemas

router = APIRouter(
    prefix="/users",
    tags=["Users"]
)

@router.get("/me", response_model=schemas.UserResponse)
async def read_users_me(current_user: user_models.User = Depends(get_current_active_user)):
    """
    Get current logged in user information.
    """
    return current_user
