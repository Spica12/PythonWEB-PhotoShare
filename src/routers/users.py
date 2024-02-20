from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db
from src.schemas.users import UserResponse, UserUpdate, AnotherUsers
from src.services.auth import auth_service
from src.models.users import UserModel
router_users = APIRouter(prefix="/users", tags=["Users"])


@router_users.get("/{username}", response_model=AnotherUsers)
async def get_user(username: str, db: AsyncSession = Depends(get_db)):
    # Endpoint to retrieve the profile information of a specific user by username.
    user_info = await UserRepo(db).get_user_by_username(username)
    if not user_info:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found.")
    return user_info


@router_users.put("/{username}", response_model=None, dependencies=None, status_code=None)
async def update_user(db: AsyncSession = Depends(get_db)):
    """
    Method put for username only if admin. Depends will be later.

    All depends will be later

    Need model with fields: is_active, role
    Show everything about user (excludes password), can change only: is_active, role
    """
    pass


@router_users.get("/my_profile", response_model=UserResponse)
async def get_current_user(user: UserModel = Depends(auth_service.get_current_user), db: AsyncSession = Depends(get_db)):
    """
    Endpoint to retrieve the information of the currently authenticated user.

    All depends will be later

    Need model with all fields excludes password, is_active. Can show the user role (admin|moderator|user).
    """
    user = await auth_service.get_user_by_email(email=user.email, db=db)

    user_response = UserResponse(
        username=user.username,
        email=user.email,
        avatar=user.avatar,
        role=user.role,
        picture_count=user.picture_count,
        created_at=user.created_at
    )

    return user_response


@router_users.put("/my_profile", response_model=None, dependencies=None, status_code=None)
async def update_current_user():
    """
    Show profile of current user. Depends will be later.

    All depends will be later

    Need model with all fields excluded is_active, role
    """
    pass
