from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db
from src.schemas.users import UserResponse, UserUpdate, AnotherUsers, UserUpdateEmail
from src.services.auth import auth_service

from src.models.users import UserModel, Roles
from src.services.auth import AuthService

router_users = APIRouter(prefix="/users", tags=["Users"])


@router_users.get("/my_profile", response_model=UserResponse)
async def get_current_user(
        user: UserModel = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db),
):
    """
    Endpoint to retrieve the information of the currently authenticated user.

    All depends will be later

    Need model with all fields excludes password, is_active. Can show the user role (admin|moderator|user).
    """
    return user


@router_users.get("/{username}", response_model=UserResponse)
async def get_user(
        username: str,
        current_user: UserModel = Depends(get_current_user),
        auth_service: AuthService = Depends(),
        db: AsyncSession = Depends(get_db),
):
    """
    Endpoint to retrieve the profile information of a specific user by username.
    """
    # перевірка чи користувач авторизований
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication required"
        )

        # Отримання профілю користувача
    user_info = await auth_service.get_user_by_username(username, db)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )

    return user_info


def is_admin(user: UserModel = Depends(auth_service.get_current_user)):
    if user.role != Roles.admin:
        raise HTTPException(status_code=403, detail="You do not have permission to access this resource.")
    return user


@router_users.put(
    "/{username}", response_model=bool)
async def admin_manipulation(username: str, is_active: bool, confirmed: bool, role: Roles, db: AsyncSession = Depends(get_db), current_user: UserModel = Depends(is_admin)):
    """
    Method put for username only if admin. Depends will be later.

    All depends will be later

    Need model with fields: is_active, role
    Show everything about user (excludes password), can change only: is_active, role
    """
    await auth_service.admin_manipulation(username, is_active, confirmed, role, db)
    return True


@router_users.put("/my_profile", response_model=UserResponse)
async def update_current_user(
        user_update: UserUpdateEmail,
        current_user: UserModel = Depends(auth_service.get_current_user),
        db: AsyncSession = Depends(get_db)
):
    """
    Update the current user's email and/or avatar.
    """
    if not current_user:
        raise HTTPException(status_code=401, detail="User not authenticated")

    auth_service = AuthService()

    if user_update.new_email:
        current_user.email = user_update.new_email

    if user_update.new_avatar:
        current_user.avatar = str(user_update.new_avatar)  # Convert Url object to string

    try:
        await db.commit()
        return {"message": "User profile updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to update user profile: {e}")


@router_users.get("/users/{username}")
async def redirect_to_my_profile(username: str, current_user: UserModel = Depends(auth_service.get_current_user),
                                 db: AsyncSession = Depends(get_db)):
    if username == current_user.username:
        return RedirectResponse(status_code=status.HTTP_302_FOUND, url="/")
    user = await auth_service.get_user_by_username(username, db)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return user
