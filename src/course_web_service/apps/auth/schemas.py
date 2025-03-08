import datetime
import uuid

from pydantic import BaseModel, EmailStr, Field, field_validator


class GetUserByID(BaseModel):
    """Схема для получения пользователя по ID."""

    id: uuid.UUID | str

    @field_validator("id")
    def validate_uuid(cls, value):
        if isinstance(value, str):
            try:
                uuid.UUID(value)
            except ValueError:
                raise ValueError("Некорректный UUID.")
        return value

    class Config:
        json_encoders = {
            uuid.UUID: lambda v: str(v),
        }


class GetUserByEmail(BaseModel):
    """Схема для получения пользователя по email."""

    email: EmailStr


class RegisterUser(GetUserByEmail):
    """Схема для регистрации пользователя."""

    password: str = Field(..., min_length=8, description="Пароль должен быть не менее 8 символов.")


class CreateUser(GetUserByEmail):
    """Схема для создания пользователя в базе данных."""

    hashed_password: str


class UserReturnData(GetUserByEmail, GetUserByID):
    """Схема для возврата данных о пользователе."""

    is_active: bool = Field(..., description="Активен ли пользователь.")
    is_superuser: bool = Field(..., description="Является ли пользователь суперпользователем.")
    is_verified: bool = Field(..., description="Подтвержден ли email пользователя.")
    created_at: datetime.datetime = Field(..., description="Дата и время создания пользователя.")
    updated_at: datetime.datetime = Field(
        ..., description="Дата и время последнего обновления пользователя."
    )

    class Config:
        json_encoders = {
            datetime.datetime: lambda v: v.isoformat(),
        }


class UserInDB(BaseModel):
    """Схема для хранения пользователя в базе данных."""

    id: uuid.UUID
    email: EmailStr
    hashed_password: str
    is_active: bool
    is_superuser: bool
    is_verified: bool
    created_at: datetime.datetime
    updated_at: datetime.datetime

    class Config:
        json_encoders = {
            uuid.UUID: lambda v: str(v),
            datetime.datetime: lambda v: v.isoformat(),
        }


class Token(BaseModel):
    """Схема для возврата токена."""

    access_token: str = Field(..., description="JWT токен для аутентификации.")
    refresh_token: str = Field(..., description="Токен для обновления access-токена.")
    token_type: str = Field(..., description="Тип токена (обычно 'bearer').")
