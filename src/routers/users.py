from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf import messages
from src.dependencies.database import get_db
from src.models.users import Roles, UserModel
from src.schemas.users import (UserUpdateAvatarSchema, UserMyResponseSchema, UserResponseExtendedSchema,
                               UserUpdateByAdminSchema, UserUpdateEmailSchema, UserAdminResponseSchema)
from src.services.auth import auth_service
from src.services.photos import PhotoService
from src.services.cloudinary import CloudinaryService
from src.services.roles import RoleChecker

router_users = APIRouter(prefix="/users", tags=["Users"])


@router_users.get("/my_profile",
                  response_model=UserMyResponseSchema
                  )
async def get_current_user(
    current_user: UserModel = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Endpoint to retrieve the information of the currently authenticated user.

    Can show the user role (admin|moderator|user).
    """
    # to view how many photos user have
    # picture_count = await PhotoService(db).get_photo_count(user_id=current_user.id)
    #
    # return UserMyResponseSchema(username=current_user.username,
    #                             email=current_user.email,
    #                             avatar=current_user.avatar,
    #                             role=current_user.role,
    #                             picture_count=picture_count,
    #                             created_at=current_user.created_at
    #                             )
    return current_user


@router_users.put(
    "/my_profile/email",
    response_model=UserMyResponseSchema,
    dependencies=None,
    status_code=None
)
async def update_email_current_user(
    body: UserUpdateEmailSchema = Depends(),
    current_user: UserModel = Depends(auth_service.get_current_user),
    db: AsyncSession = Depends(get_db),
):
    exist_user_by_email = await auth_service.get_user_by_email(body.email, db=db)
    if exist_user_by_email:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=messages.EMAIL_IS_ALREADY_BUSY
        )

    if not auth_service.verify_password(body.confirm_password, current_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_PASSWORD
        )

    if body.email:
        current_user = await auth_service.change_email(current_user.id, body.email, db)

    return current_user


@router_users.put(
    "/my_profile/avatar",
    response_model=UserMyResponseSchema,
    dependencies=None,
    status_code=None
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


@router_users.get("/{username}",
                  response_model=UserResponseExtendedSchema,
                  dependencies=[Depends(RoleChecker([Roles.admin, Roles.moderator, Roles.users]))]
                  )
async def get_user(
    username: str,
    db: AsyncSession = Depends(get_db),
):
    """
    Endpoint to retrieve the profile information of a specific user by username.
    """
    user_info = await auth_service.get_user_by_username(username, db)
    if not user_info:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.ACCOUNT_NOT_FOUND
        )
    # to view how many photos user have
    picture_count = await PhotoService(db).get_photo_count(user_id=user_info.id)

    return UserResponseExtendedSchema(username=user_info.username,
                                      avatar=user_info.avatar,
                                      role=user_info.role,
                                      picture_count=picture_count,
                                      is_active=user_info.is_active,
                                      confirmed=user_info.confirmed,
                                      created_at=user_info.created_at)


@router_users.put(
    "/{username}",
    response_model=UserAdminResponseSchema,
    dependencies=[Depends(RoleChecker([Roles.admin]))],
)
async def update_user(
    username: str,
    body: UserUpdateByAdminSchema = Depends(),
    db: AsyncSession = Depends(get_db)
):
    """
    Method put for username only if admin.

    Show everything about user (excludes password), can change only: is_active, role
    """
    user = await auth_service.get_user_by_username(username, db)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail=messages.ACCOUNT_NOT_FOUND
        )
    user = await auth_service.update_user_by_admin(user.id, body, db)

    return user
