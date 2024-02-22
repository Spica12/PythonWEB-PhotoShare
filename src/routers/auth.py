from fastapi import APIRouter, HTTPException, Security, status, Depends, BackgroundTasks, Request
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.security import HTTPAuthorizationCredentials, OAuth2PasswordRequestForm, HTTPBearer
from src.models.users import UserModel

from src.dependencies.database import get_db

from src.schemas.users import UserSchema, UserResponse, TokenSchema, RequestEmail
from src.services.auth import auth_service
from src.services.email import EmailService
from src.conf import messages
from src.repositories.users import UserRepo

router_auth = APIRouter(prefix="/auth", tags=["Auth"])
get_refresh_token = HTTPBearer()


@router_auth.post(
    "/register", response_model=UserResponse, status_code=status.HTTP_201_CREATED
)
async def register(body: UserSchema, request: Request, bt: BackgroundTasks, db: AsyncSession = Depends(get_db)):
    # need response model and body schema
    exist_user = await auth_service.get_user_by_email(body.email, db=db)
    if exist_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT, detail=messages.ACCOUNT_EXIST
        )

    body.password = auth_service.get_password_hash(body.password)
    new_user = await auth_service.create_user(body, db)

    bt.add_task(
        EmailService().send_varification_mail, new_user.email, new_user.username, str(request.base_url)
    )
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
    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=messages.ACCOUNT_BLOCKED,
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
    access_token = await auth_service.create_access_token(user.email)
    refresh_token = await auth_service.create_refresh_token(user.email)

    await auth_service.update_refresh_token(user, refresh_token, db)

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
    }


@router_auth.get("/logout")
async def logout():
    pass


@router_auth.get("/refresh", response_model=TokenSchema)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(get_refresh_token),
                        db: AsyncSession = Depends(get_db)):
    token = credentials.credentials
    email = await auth_service.get_email_from_token(token)
    user = await auth_service.get_user_by_email(email, db)
    refresh_token = await auth_service.get_refresh_token_by_user(user, db)
    if refresh_token.token != token:
        await auth_service.update_refresh_token(user, None, db)
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=messages.INVALID_REFRESH_TOKEN)

    access_token = await auth_service.create_access_token(user.email)
    refresh_token = await auth_service.create_refresh_token(user.email)
    await auth_service.update_refresh_token(user, refresh_token, db)

    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router_auth.get("/confirmed_email/{token}")
async def confirm_email(token: str, db: AsyncSession = Depends(get_db)):
    email = await auth_service.get_email_from_token(token)
    user = await auth_service.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=messages.VERIFICATION_ERROR)
    if user.confirmed:
        return {"message": messages.EMAIL_ALREADY_CONFIRMED}
    await auth_service.confirmed_email(user, db)
    return {"message": messages.EMAIL_CONFIRMED}


# @router_auth.post('/request_email')
# async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
#                         db: AsyncSession = Depends(get_db)):
#     user = await auth_service.get_user_by_email(body.email, db)

#     if user.confirmed:
#         return {"message": "Your email is already confirmed"}
#     if user:
#         background_tasks.add_task(email_service, user.email, user.username, str(request.base_url))
#     return {"message": "Check your email for confirmation."}
