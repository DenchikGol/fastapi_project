import logging
import uuid

from fastapi import APIRouter, Depends, status

from course_web_service.apps.auth_app.security import oauth2_scheme
from course_web_service.apps.user_app.schemas import (
    DeleteUserResponse,
    UpdateUser,
    UserReturnData,
)
from course_web_service.apps.user_app.services import UserService

logger = logging.getLogger(__name__)

user_router = APIRouter(prefix="/users", tags=["users"])


@user_router.get("/{user_id}", response_model=UserReturnData, status_code=status.HTTP_200_OK)
async def read_user_info(
    user_id: uuid.UUID | str,
    token: str = Depends(oauth2_scheme),
    service: UserService = Depends(UserService),
):
    """Возвращает данные пользователя."""

    return await service.get_user_or_403(token=token, user_id=user_id)


@user_router.patch("/{user_id}", response_model=UserReturnData)
async def update_current_user(
    user_id: uuid.UUID | str,
    update_data: UpdateUser,
    service: UserService = Depends(UserService),
    token: str = Depends(oauth2_scheme),
):
    """Обновляет данные текущего пользователя."""
    return await service.update_user(token=token, user_id=user_id, update_data=update_data)


@user_router.delete("/{user_id}", response_model=DeleteUserResponse)
async def delete_current_user(
    user_id: uuid.UUID | str,
    service: UserService = Depends(UserService),
    token: str = Depends(oauth2_scheme),
):
    """Удаляет текущего пользователя."""
    return await service.delete_user(token=token, user_id=user_id)
