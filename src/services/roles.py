from typing import List

from fastapi import Depends, HTTPException, Request, status

from src.models.users import Roles, UserModel
from src.services.auth import auth_service


class RoleChecker:
    def __init__(self, allowed_roles: List[Roles]):
        self.allowed_roles = allowed_roles

    async def __call__(self, request: Request, current_user: UserModel = Depends(auth_service.get_current_user)):
        if current_user.roles not in self.allowed_roles:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Operation forbidden")
