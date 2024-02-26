from fastapi import APIRouter, Depends, HTTPException, Security, status
from sqlalchemy.ext.asyncio import AsyncSession
from src.services.cloudinary import CloudinaryService
from src.services.roles import RoleChecker

from src.dependencies.database import get_db
from src.schemas.users import (
    UserResponse,
    UserUpdateEmailSchema,
    UserUpdateAvatarSchema,
    AnotherUsers,
)
from src.services.auth import auth_service
from src.models.users import Roles, UserModel
from src.services.auth import AuthService
from src.conf import messages

router_users = APIRouter(prefix="/users", tags=["Users"])


@router_users.get("/my_profile", response_model=UserResponse)
async def get_current_user(
    current_user: UserModel = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Endpoint to retrieve the information of the currently authenticated user.
    All depends will be later
    Need model with all fields excludes password, is_active. Can show the user role (admin|moderator|user).
    """
    return current_user


# lefosir704@lendfash.com


@router_users.put(
    "/my_profile/email", response_model=None, dependencies=None, status_code=None
)
async def update_email_current_user(
    body: UserUpdateEmailSchema = Depends(),
    current_user: UserModel = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not auth_service.verify_password(body.confirm_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_PASSWORD
        )

    if body.email:
        current_user = await auth_service.change_email(current_user.id, body.email, db)
    # if body.old_password and body.new_password:
    #     if body.old_password != body.confirm_password:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail=messages.OLD_AND_NEW_PASSWORD_NOT_MATCH,
    #         )
    #     body.confirm_password = auth_service.get_password_hash(body.confirm_password)
    #     current_user = await auth_service.update_password(
    #         current_user.id, body.confirm_password, db
    #     )

    # if body.avatar:
    #     photo_cloud_url = CloudinaryService().upload_avatar(body.file, current_user.id)
    #     current_user = await auth_service.update_avatar(
    #         current_user.id, photo_cloud_url, db
    #     )

    return current_user


@router_users.put(
    "/my_profile/avatar", response_model=None, dependencies=None, status_code=None
)
async def update_avatar_current_user(
    body: UserUpdateAvatarSchema = Depends(),
    current_user: UserModel = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if not auth_service.verify_password(body.confirm_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_PASSWORD
        )

    if body.avatar:
        photo_cloud_url = CloudinaryService().upload_avatar(
            body.avatar, current_user.id
        )
        current_user = await auth_service.update_avatar(
            current_user.id, photo_cloud_url, db
        )

    return current_user


@router_users.get("/{username}", response_model=UserResponse)
async def get_user(
    username: str,
    db: AsyncSession = Depends(get_db),
    auth_service: AuthService = Depends(),
    current_user: UserModel = Depends(auth_service.get_current_user),
):
    """
    Endpoint to retrieve the profile information of a specific user by username.
    """
    user_info = await auth_service.get_user_by_username(username, db)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.ACCOUNT_NOT_FOUND
        )
    return user_info


@router_users.put(
    "/{username}",
    response_model=None,
    dependencies=[Depends(RoleChecker([Roles.admin]))],
)
async def update_user(db: AsyncSession = Depends(get_db)):
    """
    Method put for username only if admin. Depends will be later.

    All depends will be later

    Need model with fields: is_active, role
    Show everything about user (excludes password), can change only: is_active, role
    """
    return {"message": "ok"}
