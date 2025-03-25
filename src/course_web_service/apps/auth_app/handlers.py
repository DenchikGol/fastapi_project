import logging
from datetime import UTC, datetime, timedelta

import jwt
from fastapi import HTTPException, status
from passlib.context import CryptContext

from course_web_service.core.settings import settings

logger = logging.getLogger(__name__)


class AuthHandler:
    """Класс для обработки аутентификации: хэширование паролей, создание и валидация токенов."""

    secret = settings.auth_settings.secret_key.get_secret_value()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    algorithm = settings.auth_settings.algorithm

    async def get_password_hash(self, password: str) -> str:
        """Хэширует пароль."""
        return self.pwd_context.hash(password)

    async def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Проверяет, соответствует ли пароль хэшу."""
        return self.pwd_context.verify(plain_password, hashed_password)

    async def create_access_token(self, data: dict, expires_delta: timedelta | None = None):
        """Создает access-токен."""
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(
                minutes=settings.auth_settings.access_token_expire_minutes
            )
        return await self._create_token(data=data, expire=expire)

    async def decode_token(self, token: str, token_type_for_logger: str) -> dict:
        """Декодирует access-токен."""
        try:
            payload = jwt.decode(token, self.secret, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            logger.warning(f"{token_type_for_logger} token has expired.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Token has expired.",
            ) from None
        except jwt.InvalidTokenError:
            logger.warning(f"Invalid {token_type_for_logger} token.")
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token.",
            ) from None

    async def create_refresh_token(self, data: dict, expires_delta: timedelta | None = None) -> str:
        """Создает refresh-токен."""
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(
                days=settings.auth_settings.refresh_token_expire_days
            )
        return await self._create_token(data=data, expire=expire)

    async def _create_token(
        self,
        data: dict,
        expire: datetime,
    ) -> str:
        """Общий метод для создания токенов."""
        to_encode = data.copy()
        to_encode.update({"exp": expire})
        return jwt.encode(payload=to_encode, key=self.secret, algorithm=self.algorithm)
