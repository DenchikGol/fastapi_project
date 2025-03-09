import logging

from fastapi import Depends, HTTPException, status
from sqlalchemy import delete, insert, select, update
from sqlalchemy.exc import IntegrityError

from course_web_service.apps.auth.schemas import (
    CreateUser,
    DeleteUserResponse,
    GetUserByEmail,
    UpdateUserToDB,
    UserInDB,
    UserReturnData,
)
from course_web_service.core.core_dependecy.db_dependency import DBDependency
from course_web_service.database.models.user import User

logger = logging.getLogger(__name__)


class UserManager:
    """Класс для управления пользователями: создание и поиск."""

    def __init__(self, model: type[User] = User, db: DBDependency = Depends(DBDependency)) -> None:
        """Инициализирует менеджер пользователей."""
        self.db = db
        self.model = model

    async def create_user(self, user: CreateUser) -> UserReturnData:
        """Создает нового пользователя."""
        logger.info(f"Starting writing new user to DB: {user.email}")
        async with self.db.db_session() as session:
            query = insert(self.model).values(**user.model_dump()).returning(self.model)

            try:
                result = await session.execute(query)
                await session.commit()
            except IntegrityError:
                logger.error(f"User already exists: {user.email}")
                raise HTTPException(
                    status_code=status.HTTP_409_CONFLICT, detail="User already exists."
                ) from None

            user_data = result.scalars().first()
            logger.info(f"User {user.email} created successfully.")
            return UserReturnData(**user_data.__dict__)

    async def get_user_by_email(self, user: GetUserByEmail) -> UserInDB:
        """Возвращает пользователя по email."""
        async with self.db.db_session() as session:
            query = select(self.model).filter(self.model.email == user.email)

            try:
                result = await session.execute(query)
            except Exception as e:
                logger.error(f"Error fetching user by email: {e}", exc_info=True)
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST, detail=str(e)
                ) from None

            user_data = result.scalars().first()

            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found.",
                )

            return UserInDB(**user_data.__dict__)

    async def update_user_info(
        self, user_email: str, update_data: UpdateUserToDB
    ) -> UserReturnData:
        """Обновляет данные пользователя в базе данных."""
        logger.info(f"Updating user with email: {user_email}")
        async with self.db.db_session() as session:
            query = (
                update(self.model)
                .where(self.model.email == user_email)
                .values(**update_data.model_dump(exclude_unset=True))
                .returning(self.model)
            )
            result = await session.execute(query)
            await session.commit()
            user_data = result.scalars().first()
            if not user_data:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found.",
                )
            return UserReturnData(**user_data.__dict__)

    async def delete_user(self, user_email: str) -> DeleteUserResponse:
        """Удаляет пользователя из базы данных."""
        logger.info(f"Deleting user with email: {user_email}")
        async with self.db.db_session() as session:
            query = delete(self.model).where(self.model.email == user_email)
            result = await session.execute(query)
            await session.commit()
            if result.rowcount == 0:
                raise HTTPException(
                    status_code=status.HTTP_404_NOT_FOUND,
                    detail="User not found.",
                )
            return DeleteUserResponse(message="User deleted successfully.")
