from fastapi import APIRouter, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from src.dependencies.database import get_db

router_auth = APIRouter(prefix="/auth", tags=["Auth"])


@router_auth.post("/register", response_model=None, status_code=status.HTTP_201_CREATED)
async def register(body, db: AsyncSession = Depends(get_db)):
    # need response model and body schema
    pass


@router_auth.post("/login", response_model=None)
async def login(body: OAuth2PasswordRequestForm = Depends(), db: AsyncSession = Depends(get_db)):
    # need response model
    pass


@router_auth.get("/logout")
async def logout():
    pass


@router_auth.get("/refresh_token", response_model="")
async def refresh_token(credentials, db: AsyncSession = Depends(get_db)):
    # need response model, credentials
    pass
