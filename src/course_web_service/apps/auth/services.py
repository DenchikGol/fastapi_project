import datetime
import logging

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from course_web_service.apps.auth.enums import JWTTokenTypeForLogging
from course_web_service.apps.auth.handlers import AuthHandler
from course_web_service.apps.auth.managers import UserManager
from course_web_service.apps.auth.schemas import (
    CreateUser,
    DeleteUserResponse,
    GetUserByEmail,
    RegisterUser,
    Token,
    UpdateUser,
    UpdateUserToDB,
    UserReturnData,
)

logger = logging.getLogger(__name__)


class UserService:
    """Класс для управления пользователями: регистрация, аутентификация, управление токенами."""

    def __init__(
        self,
        manager: UserManager = Depends(UserManager),
        auth: AuthHandler = Depends(AuthHandler),
    ):
        """Инициализирует сервис пользователей."""
        self.auth = auth
        self.manager = manager

    async def register_user(self, user: RegisterUser) -> UserReturnData:
        """Регистрирует нового пользователя."""
        logger.info(f"Starting registration for user: {user.email}")
        try:
            hashed_password = await self.auth.get_password_hash(user.password)
            new_user = CreateUser(email=user.email, hashed_password=hashed_password)

            return await self.manager.create_user(user=new_user)
        except Exception as e:
            logger.error(f"Failed to register user {user.email}: {e}", exc_info=True)
            raise

    async def authenticate_user(self, auth_for_user: RegisterUser) -> UserReturnData:
        """Аутентифицирует пользователя."""
        logger.info(f"Authenticating user: {auth_for_user.email}")
        try:
            user = await self.manager.get_user_by_email(GetUserByEmail(email=auth_for_user.email))
            if not user or not await self.auth.verify_password(
                auth_for_user.password, user.hashed_password
            ):
                logger.warning(f"Authentication failed for user: {auth_for_user.email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password.",
                )
            logger.info(f"User {auth_for_user.email} authenticated successfully.")

            return UserReturnData(**user.model_dump())
        except Exception as e:
            logger.error(
                f"Error during authentication for user {auth_for_user.email}: {e}", exc_info=True
            )
            raise

    async def get_current_user(self, token: Token) -> UserReturnData:
        """Возвращает текущего пользователя по токену."""
        payload = await self.auth.decode_token(
            token=token.access_token, token_type_for_logger=JWTTokenTypeForLogging.ACCESS
        )
        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token.",
            )
        user = await self.manager.get_user_by_email(GetUserByEmail(email=email))

        return UserReturnData(**user.model_dump())

    async def login_for_access_token(
        self, form_data: OAuth2PasswordRequestForm = Depends()
    ) -> dict:
        """Создает access- и refresh-токены для пользователя."""
        user = await self.authenticate_user(
            RegisterUser(email=form_data.username, password=form_data.password)
        )
        access_token = await self.auth.create_access_token(data={"sub": user.email})
        refresh_token = await self.auth.create_refresh_token(data={"sub": user.email})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def refresh_access_token(self, refresh_token: str):
        """Обновляет access-токен с помощью refresh-токена."""
        payload = await self.auth.decode_token(
            refresh_token, token_type_for_logger=JWTTokenTypeForLogging.REFRESH
        )
        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token.",
            )

        access_token = await self.auth.create_access_token(data={"sub": email})

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def update_current_user(self, token: str, update_data: UpdateUser) -> UserReturnData:
        """Обновляет данные пользователя."""
        user = await self.get_current_user(token)
        logger.info(f"Updating user with email: {user.email}")
        update_user = UpdateUserToDB(**user.model_dump())
        if update_data.password:
            update_user.hashed_password = await self.auth.get_password_hash(update_data.password)
        update_user.updated_at = datetime.UTC
        return await self.manager.update_user_info(user_email=user.email, update_data=update_user)

    async def delete_current_user(self, token: str) -> DeleteUserResponse:
        """Удаляет пользователя."""
        user = await self.get_current_user(token)
        logger.info(f"Deleting user with email: {user.email}")
        return await self.manager.delete_user(user_email=user.email)
