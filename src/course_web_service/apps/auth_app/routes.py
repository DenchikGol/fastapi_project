import logging

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from course_web_service.apps.auth_app.schemas import Token
from course_web_service.apps.auth_app.services import AuthService
from course_web_service.apps.user_app.schemas import RegisterUser, UserReturnData

logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post(
    path="/register",
    response_model=UserReturnData,
    status_code=status.HTTP_201_CREATED,
)
async def registration(
    user: RegisterUser,
    service: AuthService = Depends(AuthService),
) -> UserReturnData:
    """Регистрирует нового пользователя."""
    return await service.register_user(user=user)


@auth_router.post(path="/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: AuthService = Depends(AuthService),
) -> dict:
    """Создает access- и refresh-токены для пользователя."""
    return await service.login_for_access_token(form_data=form_data)


@auth_router.post("/refresh", response_model=Token)
async def refresh_access_token(
    refresh_token: str,
    service: AuthService = Depends(AuthService),
):
    """Обновляет access-токен с помощью refresh-токена."""
    return await service.refresh_access_token(refresh_token=refresh_token)
