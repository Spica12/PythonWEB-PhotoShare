from typing import List

from fastapi import Depends, HTTPException, Request, status

from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from src.conf import messages
from src.models.users import Roles, UserModel
from src.services.auth import auth_service
from src.repositories.users import UserRepo


class RoleChecker:
    def __init__(self, allowed_roles: List[Roles]):
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, current_user: UserModel = Depends(auth_service.get_current_user)):
        if current_user.role not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=messages.OPERATION_FORBIDDEN)

    async def get_user_role(self, user_id: UUID, db: AsyncSession):
        user = await UserRepo(db).get_user_by_id(user_id=user_id)
        return user.role

    async def check_admin_or_moderator(self, user_id: UUID, db: AsyncSession):
        """
        Usage example:
        RoleChecker([Roles.admin, Roles.moderator]).check_admin_or_moderator(user_id=current_user.id, db=db)

        in base code check only if not None => moderator or administrator role

        To check admin or moderator separately -> use only [Roles.admin] or [Roles.moderator]
        """
        user = await UserRepo(db).get_user_by_id(user_id=user_id)
        if user.role in self.allowed_roles:
            return user.role
        else:
            return None
