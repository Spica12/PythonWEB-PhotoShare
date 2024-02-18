from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.dependencies.database import get_db

router_users = APIRouter(prefix="/users", tags=["Users"])


@router_users.get("/{username}", response_model=None, dependencies=None, status_code=None)
async def get_user(db: AsyncSession = Depends(get_db)):
    """
    Show info about user by username

    All depends will be later
    """
    pass


@router_users.put("/{username}", response_model=None, dependencies=None, status_code=None)
async def update_user(db: AsyncSession = Depends(get_db)):
    """
    Method put for username only if admin. Depends will be later.

    All depends will be later

    Need model with fields: is_active, role
    Show everything about user (excludes password), can change only: is_active, role
    """
    pass


@router_users.get("/my_profile", response_model=None, dependencies=None, status_code=None)
async def get_current_user(db: AsyncSession = Depends(get_db)):
    """
    Show profile of current user. Depends will be later.

    All depends will be later

    Need model with all fields excludes password, is_active. Can show the user role (admin|moderator|user).
    """
    pass


@router_users.put("/my_profile", response_model=None, dependencies=None, status_code=None)
async def update_current_user():
    """
    Show profile of current user. Depends will be later.

    All depends will be later

    Need model with all fields excluded is_active, role
    """
    pass
