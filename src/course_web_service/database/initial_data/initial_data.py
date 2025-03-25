import logging
from pathlib import Path

import yaml
from passlib.context import CryptContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from course_web_service.apps.user_app.schemas import RoleSchema, UserInDB
from course_web_service.core.settings import settings
from course_web_service.database.models.user import Role, User

logger = logging.getLogger(__name__)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class InitialDataLoader:
    def __init__(self, data_dir: Path = Path("src/course_web_service/database/initial_data")):
        self.data_dir = data_dir

    async def load_roles(self, session: AsyncSession) -> None:
        """Загружает роли из YAML в базу, если их нет."""
        file_path = self.data_dir / "roles.yaml"
        data = yaml.safe_load(file_path.read_text())

        for role_data in data["roles"]:
            role = RoleSchema(**role_data)

            exists = await session.execute(select(Role).where(Role.name == role.name))
            if not exists.scalar():
                session.add(Role(**role.model_dump()))
                logger.info(f"Добавлена роль: {role.name}")

        await session.commit()

    async def load_users(self, session: AsyncSession) -> None:
        """Загружает пользователей из YAML, хешируя пароли."""
        file_path = self.data_dir / "users.yaml"
        data = yaml.safe_load(file_path.read_text())

        users_credentials = [
            settings.init_app_settings.admin_email,
            settings.init_app_settings.admin_password.get_secret_value(),
            settings.init_app_settings.manager_email,
            settings.init_app_settings.manager_password.get_secret_value(),
        ]

        for user_data in data["users"]:
            user_data["email"] = users_credentials.pop(0)
            user_data["hashed_password"] = pwd_context.hash(users_credentials.pop(0))

            user = UserInDB(**user_data)

            exists = await session.execute(select(User).where(User.email == user.email))
            if not exists.scalar():
                session.add(User(**user.model_dump()))
                logger.info(f"Добавлен пользователь: {user.email}")

        await session.commit()

    async def load_all(self, session: AsyncSession) -> None:
        """Загружает все начальные данные."""
        await self.load_roles(session)
        await self.load_users(session)
