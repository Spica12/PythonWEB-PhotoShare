from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db
from src.schemas.users import UserResponse, UserUpdate, AnotherUsers
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
    if user.role != Roles.admin or user.role != Roles.moderator:
        raise HTTPException(status_code=403, detail="You do not have permission to access this resource.")
    return user


@router_users.put(
    "/{username}/ban", response_model=bool, dependencies=[Depends(is_admin)]
)
async def ban_user(username: str, db: AsyncSession = Depends(get_db)):
    """
    Method put for username only if admin. Depends will be later.

    All depends will be later

    Need model with fields: is_active, role
    Show everything about user (excludes password), can change only: is_active, role
    """
    await auth_service.ban_user(username, db)
    return True


@router_users.put("/my_profile", summary="Change password for a logged in user")
async def update_current_user(user_change_password_body: UserUpdate,
                              user: UserModel = Depends(auth_service.get_current_user),
                              db: AsyncSession = Depends(get_db)):
    """
    Show profile of current user. Depends will be later.

    All depends will be later

    Need model with all fields excluded is_active, role
    """
    try:
        auth_service.update_user(user.email, user_change_password_body.new_password, db)
        return {"result": f"{user.username}, your password has been updated!"}
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, detail=f"{e}")  # Помилка клієнта: неправильні дані запиту
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail=f"An unexpected error occurred. Report this "
                                                                     f"message to support: {e}")  # Помилка клієнта:
        # внутрішня помилка сервера

# @router_users.get("/users/{username}")
# async def get_user_profile(username: str, current_user: UserModel = Depends(auth_service.get_current_user),
#                             db: AsyncSession = Depends(get_db)):
#     if username == current_user.username:
#         return {"message": "Redirecting to your profile..."}
#     user = await auth_service.get_user_by_username(username, db)
#     if not user:
#         raise HTTPException(status_code=404, detail="User not found.")
#     return user
