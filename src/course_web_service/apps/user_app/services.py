import logging
import uuid

from fastapi import HTTPException, status

from course_web_service.apps.auth_app.services import AuthService
from course_web_service.apps.user_app.enums import PermissionsUserChange
from course_web_service.apps.user_app.schemas import (
    DeleteUserResponse,
    GetUserByID,
    UpdateUser,
    UpdateUserToDB,
    UserReturnData,
)

logger = logging.getLogger(__name__)


class UserService(AuthService):
    """Класс для управления пользователями: регистрация, обновление, удаление."""

    async def get_user_or_403(self, token: str, user_id: uuid.UUID | str):
        current_user = await self.get_current_user(token=token)
        user_what_you_wanna = await self.manager.get_user_by_id(user=GetUserByID(user_id))
        if (
            current_user.role not in PermissionsUserChange._value2member_map_.keys()
            or current_user.email != user_what_you_wanna.email
        ):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied.",
            )

        return UserReturnData(**user_what_you_wanna.model_dump())

    async def update_user(
        self,
        token: str,
        user_id: uuid.UUID | str,
        update_data: UpdateUser,
    ) -> UserReturnData:
        """Обновляет данные пользователя."""
        user_what_you_wanna = await self.manager.get_user_by_id(user=GetUserByID(user_id))
        current_user = await self.get_current_user(token=token)
        if current_user.role not in PermissionsUserChange._value2member_map_.keys():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied.",
            )
        logger.info(f"Updating user with email: {user_what_you_wanna.email}")
        update_user = UpdateUserToDB(email=user_what_you_wanna.email)
        if update_data.password:
            update_user.hashed_password = await self.auth.get_password_hash(update_data.password)
        return await self.manager.update_user_info(
            user_email=user_what_you_wanna.email,
            update_data=update_user,
        )

    async def delete_user(self, token: str, user_id: uuid.UUID | str) -> DeleteUserResponse:
        """Удаляет пользователя."""
        user_what_you_wanna = await self.manager.get_user_by_id(user=GetUserByID(user_id))
        current_user = await self.get_current_user(token=token)
        if current_user.role not in PermissionsUserChange._value2member_map_.keys():
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Permission denied.",
            )
        logger.info(f"Deleting user with email: {user_what_you_wanna.email}")
        return await self.manager.delete_user(user_email=user_what_you_wanna.email)
