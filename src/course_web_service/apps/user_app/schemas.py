import uuid
from datetime import datetime

from pydantic import (
    BaseModel,
    ConfigDict,
    EmailStr,
    Field,
    field_serializer,
)


class RoleSchema(BaseModel):
    """Схема для роли пользователя."""

    id: int
    name: str
    description: str | None

    model_config = ConfigDict(from_attributes=True)


class GetUserByID(BaseModel):
    id: uuid.UUID


class GetUserByEmail(BaseModel):
    """Схема для получения пользователя по email."""

    email: EmailStr


class RegisterUser(GetUserByEmail):
    """Схема для регистрации пользователя."""

    password: str = Field(..., min_length=8, description="Пароль должен быть не менее 8 символов.")


class CreateUser(GetUserByEmail):
    """Схема для создания пользователя в базе данных."""

    hashed_password: str


class UserBase(BaseModel):
    """Базовая схема для пользователя."""

    id: uuid.UUID
    email: EmailStr
    first_name: str | None = Field(
        None,
        min_length=1,
        max_length=150,
        description="Имя пользователя.",
    )
    last_name: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="Фамилия пользователя.",
    )
    is_active: bool = Field(..., description="Активен ли пользователь.")
    is_verified: bool = Field(..., description="Подтвержден ли email пользователя.")
    role_id: int | None = Field(None, description="ID роли пользователя.")
    created_at: datetime = Field(..., description="Дата и время создания пользователя.")
    updated_at: datetime = Field(
        ..., description="Дата и время последнего обновления пользователя."
    )

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at", "updated_at")
    def serialize_datetime(self, value: datetime) -> str:
        return value.isoformat()


class UserReturnData(UserBase):
    """Схема для возврата данных о пользователе."""

    role: RoleSchema = Field(..., description="Роль пользователя.")


class UserInDB(UserBase):
    """Схема для хранения пользователя в базе данных."""

    hashed_password: str

    @field_serializer("id")
    def serialize_uuid(self, value: uuid.UUID) -> str:
        return str(value)


class BaseUpdateUser(BaseModel):
    first_name: str | None = Field(
        None,
        min_length=1,
        max_length=150,
        description="Имя пользователя.",
    )
    last_name: str | None = Field(
        None,
        min_length=1,
        max_length=255,
        description="Фамилия пользователя.",
    )

    model_config = ConfigDict(from_attributes=True)


class UpdateUser(BaseUpdateUser):
    """Схема для обновления данных пользователя."""

    password: str | None = Field(
        None, min_length=8, description="Пароль должен быть не менее 8 символов."
    )


class UpdateUserToDB(BaseUpdateUser):
    """Схема для сохранения обновленных данных пользователя в базу данных."""

    hashed_password: str


class DeleteUserResponse(BaseModel):
    """Схема для ответа после удаления пользователя."""

    message: str = Field(..., description="Сообщение об успешном удалении.")


class CuratorSchema(BaseModel):
    """Схема для куратора."""

    id: int
    user_id: uuid.UUID
    bio: str | None

    model_config = ConfigDict(from_attributes=True)
