import logging

from fastapi import APIRouter, Depends, status
from fastapi.security import OAuth2PasswordRequestForm

from course_web_service.apps.auth.schemas import RegisterUser, Token, UserReturnData
from course_web_service.apps.auth.security import oauth2_scheme
from course_web_service.apps.auth.services import UserService

logger = logging.getLogger(__name__)

auth_router = APIRouter(prefix="/auth", tags=["auth"])


@auth_router.post(
    path="/register",
    response_model=UserReturnData,
    status_code=status.HTTP_201_CREATED,
)
async def registration(
    user: RegisterUser,
    service: UserService = Depends(UserService),
) -> UserReturnData:
    """Регистрирует нового пользователя."""
    return await service.register_user(user=user)


@auth_router.post(path="/token", response_model=Token)
async def login_for_access_token(
    form_data: OAuth2PasswordRequestForm = Depends(),
    service: UserService = Depends(UserService),
) -> dict:
    """Создает access- и refresh-токены для пользователя."""
    return await service.login_for_access_token(form_data=form_data)


@auth_router.post("/refresh", response_model=Token)
async def refresh_access_token(refresh_token: str, service: UserService = Depends(UserService)):
    """Обновляет access-токен с помощью refresh-токена."""
    return await service.refresh_access_token(refresh_token=refresh_token)


@auth_router.get("/me", response_model=UserReturnData, status_code=status.HTTP_200_OK)
async def read_users_me(
    service: UserService = Depends(UserService),
    token: str = Depends(oauth2_scheme),
):
    """Возвращает данные текущего пользователя."""
    return await service.get_current_user(token)
