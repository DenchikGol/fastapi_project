import logging
from datetime import timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm

from course_web_service.apps.auth.handlers import AuthHandler
from course_web_service.apps.auth.managers import UserManager
from course_web_service.apps.auth.schemas import CreateUser, RegisterUser, UserReturnData
from course_web_service.core.settings import settings

logger = logging.getLogger(__name__)


class UserService:
    def __init__(
        self,
        manager: UserManager = Depends(UserManager),
        auth: AuthHandler = Depends(AuthHandler),
    ):
        self.auth = auth
        self.manager = manager

    async def register_user(self, user: RegisterUser) -> UserReturnData:
        logger.info(f"Starting registration for user: {user.email}")
        try:
            hashed_password = await self.auth.get_password_hash(user.password)
            new_user = CreateUser(email=user.email, hashed_password=hashed_password)

            return await self.manager.create_user(user=new_user)
        except Exception as e:
            logger.error(f"Failed to register user {user.email}: {e}")
            raise

    async def authenticate_user(self, email: str, password: str) -> UserReturnData:
        logger.info(f"Authenticating user: {email}")
        try:
            user = await self.manager.get_user_by_email(email)
            if not user or not await self.auth.verify_password(password, user.hashed_password):
                logger.warning(f"Authentication failed for user: {email}")
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Incorrect email or password.",
                )
            logger.info(f"User {email} authenticated successfully.")
            return UserReturnData(**user.model_dump())
        except Exception as e:
            logger.error(f"Error during authentication for user {email}: {e}")
            raise

    async def get_current_user(self, token: str) -> UserReturnData:
        payload = await self.auth.decode_access_token(token)
        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid token.",
            )
        user = await self.manager.get_user_by_email(email)

        return user

    async def login_for_access_token(self, form_data: OAuth2PasswordRequestForm = Depends()) -> dict:
        user = await self.authenticate_user(form_data.username, form_data.password)

        access_token = await self.auth.create_access_token(
            data={"sub": user.email},
            expires_delta=timedelta(minutes=settings.auth_settings.access_token_expire_minutes),
        )

        refresh_token = await self.auth.create_refresh_token(
            data={"sub": user.email},
            expires_delta=timedelta(days=settings.auth_settings.refrsh_token_expire_days),
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }

    async def refresh_access_token(self, refresh_token: str):
        payload = await self.auth.decode_refresh_token(refresh_token)
        email = payload.get("sub")
        if not email:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid refresh token.",
            )

        user = await self.manager.get_user_by_email(email)

        access_token = await self.auth.create_access_token(
            data={"sub": user.email},
            expires_delta=timedelta(minutes=settings.auth_settings.access_token_expire_minutes),
        )

        return {
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer",
        }
