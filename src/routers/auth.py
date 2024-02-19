from fastapi import APIRouter, HTTPException, status, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import OAuth2PasswordRequestForm

from src.dependencies.database import get_db

from src.schemas.users import UserSchema, UserResponse, TokenSchema
from src.services.auth import auth_service
from src.conf import messages

router_auth = APIRouter(prefix="/auth", tags=["Auth"])


@router_auth.post("/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED)
async def register(
    body: UserSchema,
    db: AsyncSession = Depends(get_db)):
    # need response model and body schema
    exist_user = await auth_service.get_user_by_email(body.email, db=db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=messages.ACCOUNT_EXIST
        )
    body.password = auth_service.get_password_hash(body.password)
    new_user = await auth_service.create_user(body, db)
    # background_tasks.add_task(
    #     email_service.send_verification_mail, new_user.username, request.base_url
    # )
    return new_user


@router_auth.post("/login", response_model=TokenSchema)
async def login(
    body: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db),
):
    # need response model
    user = await auth_service.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_USERNAME
        )
    if not user.confirmed:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=messages.EMAIL_NOT_CONFIRMED,
        )
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_PASSWORD
        )
    access_token = await auth_service.create_access_token(data={"sub": user.username})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.username})

    await auth_service.update_refresh_token(user, refresh_token, db)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router_auth.get("/logout")
async def logout():
    pass


@router_auth.get("/refresh", response_model="")
async def refresh_token(credentials, db: AsyncSession = Depends(get_db)):
    """
    Refresh token
    """
    # need response model, credentials
    pass


@router_auth.get("/email/{token}")
async def confirm_email(token: str, db: AsyncSession = Depends(get_db)):
    """
    Email/user confirmation
    """
    pass
